import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from dapr.ext.workflow import WorkflowActivityContext
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate_multimodal_pages
from docling_core.types.doc import ImageRefMode
from dotenv import load_dotenv

from deepbrief.services import get_object, store_bytes

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_PICTURE_API_KEY = "DOCLING_PICTURE_API_KEY"
DEFAULT_PICTURE_API_URL = os.getenv("DOCLING_PICTURE_API_URL", "https://api.openai.com/v1/chat/completions")
DEFAULT_PICTURE_API_MODEL = os.getenv("DOCLING_PICTURE_API_MODEL", "gpt-4o-mini")
DEFAULT_PICTURE_PROMPT = "Describe the image in concise factual language suitable for narration."
DEFAULT_PIPELINE_FLAGS: dict[str, Any] = {
    "enable_remote_services": True,
    "do_ocr": True,
    "do_table_structure": True,
    "do_picture_description": True,
    "do_picture_classification": True,
    "do_code_enrichment": False,
    "do_formula_enrichment": False,
    "generate_page_images": True,
    "generate_picture_images": True,
    "images_scale": 2.0,
}


def _build_picture_description_options(
    config: dict[str, Any] | None,
) -> PictureDescriptionApiOptions | None:
    """Create PictureDescriptionApiOptions using OpenAI defaults unless overridden."""
    cfg = config or {}
    api_key = cfg.get("api_key") or os.getenv(DEFAULT_PICTURE_API_KEY)
    if not api_key:
        logger.warning(
            "Picture description enabled but %s is missing; skipping remote captions.",
            DEFAULT_PICTURE_API_KEY,
        )
        return None

    url = cfg.get("url", DEFAULT_PICTURE_API_URL)
    params = dict(cfg.get("params", {}))
    params.setdefault("model", cfg.get("model", DEFAULT_PICTURE_API_MODEL))
    area_threshold = cfg.get("picture_area_threshold", 0.05)

    logger.info(
        "Picture description configured | url=%s model=%s timeout=%s concurrency=%s"
        " area_threshold=%s",
        url,
        params.get("model"),
        cfg.get("timeout", 90),
        cfg.get("concurrency", 4),
        area_threshold,
    )

    return PictureDescriptionApiOptions(
        url=url,
        params=params,
        headers={"Authorization": f"Bearer {api_key}", **cfg.get("headers", {})},
        prompt=cfg.get("prompt", DEFAULT_PICTURE_PROMPT),
        timeout=cfg.get("timeout", 90),
        concurrency=cfg.get("concurrency", 4),
        picture_area_threshold=area_threshold,
    )


def _build_pipeline_options(overrides: dict[str, Any] | None) -> PdfPipelineOptions:
    """Merge pipeline overrides with defaults tuned for multimodal extraction."""
    cfg = dict(DEFAULT_PIPELINE_FLAGS)
    if overrides:
        cfg.update(overrides)

    options = PdfPipelineOptions(
        enable_remote_services=bool(cfg["enable_remote_services"]),
        do_ocr=bool(cfg["do_ocr"]),
        do_table_structure=bool(cfg["do_table_structure"]),
        do_picture_description=bool(cfg["do_picture_description"]),
        do_picture_classification=bool(cfg["do_picture_classification"]),
        do_code_enrichment=bool(cfg["do_code_enrichment"]),
        do_formula_enrichment=bool(cfg["do_formula_enrichment"]),
        generate_page_images=bool(cfg["generate_page_images"]),
        generate_picture_images=bool(cfg["generate_picture_images"]),
        images_scale=float(cfg["images_scale"]),
    )

    picture_options = _build_picture_description_options(cfg.get("picture_description"))
    if picture_options:
        logger.info(
            "Docling picture description enabled; remote services=%s.",
            options.enable_remote_services,
        )
        options.picture_description_options = picture_options
    else:
        logger.info(
            "Docling picture description disabled; remote services flag left at %s.",
            options.enable_remote_services,
        )
        options.do_picture_description = False

    return options


def _save_optional_exports(doc, pdf_path: Path, output_cfg: dict[str, Any]) -> Path | None:
    """
    Optionally persist Docling outputs (markdown/json) locally and return the JSON path if written.
    """
    if not output_cfg:
        return None

    saved_doc_path: Path | None = None

    markdown_cfg = output_cfg.get("markdown")
    if markdown_cfg:
        target_dir = Path(markdown_cfg.get("dir", "output/docling"))
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = markdown_cfg.get("file_name") or f"{pdf_path.stem}.md"
        dest = target_dir / filename
        include_annotations = markdown_cfg.get("include_annotations", True)
        image_mode = getattr(
            ImageRefMode,
            (markdown_cfg.get("image_mode") or "REFERENCED").upper(),
            ImageRefMode.REFERENCED,
        )
        doc.save_as_markdown(
            dest,
            image_mode=image_mode,
            include_annotations=include_annotations,
            strict_text=markdown_cfg.get("strict_text", False),
        )

    json_cfg = output_cfg.get("json")
    if json_cfg:
        target_dir = Path(json_cfg.get("dir", "output/docling"))
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = json_cfg.get("file_name") or f"{pdf_path.stem}.json"
        dest = target_dir / filename
        doc.save_as_json(dest)
        saved_doc_path = dest

    doc_store_cfg = output_cfg.get("doc_store")
    if doc_store_cfg:
        target_dir = Path(doc_store_cfg.get("dir", "output/docling_store"))
        target_dir.mkdir(parents=True, exist_ok=True)
        doc_id = getattr(getattr(doc, "origin", None), "binary_hash", pdf_path.stem)
        filename = doc_store_cfg.get("file_name") or f"{doc_id}.json"
        dest = target_dir / filename
        doc.save_as_json(dest)
        saved_doc_path = dest

    return saved_doc_path


def _persist_markdown_page(
    doc_folder: str,
    page_number: int,
    content_md: str,
    markdowns_directory: Path,
    storage_prefix: str,
    persist_locally: bool,
) -> dict[str, str | None]:
    """Persist a single page markdown locally/remote and return the paths used."""
    file_path = None
    if persist_locally:
        target_dir = markdowns_directory / doc_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        local_path = target_dir / f"page_{page_number}.md"
        local_path.write_text(content_md, encoding="utf-8")
        file_path = str(local_path)

    storage_key = f"{storage_prefix}/{doc_folder}/page_{page_number}.md"
    store_bytes(storage_key, content_md.encode("utf-8"), metadata={"contentType": "text/markdown"})

    return {"file_path": file_path, "storage_key": storage_key}


def _resolve_pdf_path(file_path: str | None, storage_key: str | None) -> tuple[Path, Path | None]:
    """
    Resolve the PDF path from disk or shared storage. Returns (pdf_path, tmp_path) where tmp_path
    should be cleaned up by the caller if not None.
    """
    tmp_path: Path | None = None
    if storage_key:
        logger.info("read_pdf_v2: fetching from shared storage: %s", storage_key)
        pdf_bytes = get_object(storage_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)
        file_path = str(tmp_path)

    if not file_path:
        raise ValueError("file_path is required when storage_key is not provided.")

    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    return pdf_path, tmp_path


def read_pdf_v2(ctx: WorkflowActivityContext, input_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert a PDF into per-page markdown using Docling with visual grounding metadata.

    The activity optionally persists page markdowns locally and in shared storage, returning
    one record per page (or a single fallback record) containing text plus provenance metadata.
    """

    input_data = input_data or {}
    file_path: str | None = input_data.get("file_path")
    storage_key: str | None = input_data.get("storage_key")
    markdowns_directory = Path(input_data.get("markdowns_directory", "output/markdowns"))
    storage_prefix = input_data.get("storage_prefix", "markdowns")
    persist_locally = bool(input_data.get("persist_locally", True))

    if not file_path and not storage_key:
        raise ValueError("Either file_path or storage_key must be provided.")

    pdf_path, tmp_path = _resolve_pdf_path(file_path, storage_key)

    try:
        pipeline_options = _build_pipeline_options(input_data.get("pipeline_options"))
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        logger.info("read_pdf_v2: converting PDF %s", pdf_path)
        result = converter.convert(str(pdf_path))
        doc = result.document

        saved_doc_path = _save_optional_exports(doc, pdf_path, input_data.get("output") or {})
        markdown_args = input_data.get("markdown_args") or {}
        include_annotations = markdown_args.get("include_annotations", True)

        doc_origin = getattr(doc, "origin", None)
        doc_hash = getattr(doc_origin, "binary_hash", None)
        storage_basename = None
        if storage_key:
            storage_basename = Path(storage_key).name
            if storage_basename:
                storage_basename = storage_basename.rsplit(".", 1)[0]
        effective_doc_id = input_data.get("doc_id") or storage_basename or pdf_path.stem or doc_hash
        doc_folder = str(effective_doc_id)
        base_metadata = {
            "document_id": doc_folder,
            "source": str(pdf_path),
            "storage_key": storage_key,
            "status": getattr(result.status, "name", str(result.status)),
            "page_count": len(getattr(doc, "pages", []) or []),
            "table_count": len(getattr(doc, "tables", []) or []),
            "picture_count": len(getattr(doc, "pictures", []) or []),
            "pipeline_remote": pipeline_options.enable_remote_services,
            "stored_document_path": str(saved_doc_path) if saved_doc_path else None,
            "markdowns_directory": str(markdowns_directory),
            "markdowns_storage_prefix": storage_prefix,
        }

        records: list[dict[str, Any]] = []
        for (
            content_text,
            content_md,
            _,
            page_cells,
            page_segments,
            page,
        ) in generate_multimodal_pages(result):
            page_number = getattr(page, "page_no", 0)
            dpi = getattr(page, "_default_image_scale", 1.0) * 72
            persisted = _persist_markdown_page(
                doc_folder=doc_folder,
                page_number=page_number,
                content_md=content_md,
                markdowns_directory=markdowns_directory,
                storage_prefix=storage_prefix,
                persist_locally=persist_locally,
            )
            page_metadata = {
                "page_number": page_number,
                "page_width": getattr(getattr(page, "size", None), "width", None),
                "page_height": getattr(getattr(page, "size", None), "height", None),
                "dpi": dpi,
                "page_cells": page_cells,
                "page_segments": page_segments,
                "page_markdown_path": persisted["file_path"],
                "page_markdown_storage_key": persisted["storage_key"],
            }
            records.append(
                {
                    "text": content_md,
                    "metadata": {
                        **base_metadata,
                        **page_metadata,
                        "plain_text": content_text,
                    },
                }
            )

        if not records:
            fallback_markdown = doc.export_to_markdown(include_annotations=include_annotations)
            persisted = _persist_markdown_page(
                doc_folder=doc_folder,
                page_number=0,
                content_md=fallback_markdown,
                markdowns_directory=markdowns_directory,
                storage_prefix=storage_prefix,
                persist_locally=persist_locally,
            )
            records.append(
                {
                    "text": fallback_markdown,
                    "metadata": {
                        **base_metadata,
                        "plain_text": fallback_markdown,
                        "page_number": 0,
                        "page_markdown_path": persisted["file_path"],
                        "page_markdown_storage_key": persisted["storage_key"],
                    },
                }
            )

        return records
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
