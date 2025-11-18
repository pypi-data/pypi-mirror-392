import logging
import tempfile
from pathlib import Path
from typing import Any

from dapr.ext.workflow import WorkflowActivityContext
from dapr_agents.document.reader.pdf.pypdf import PyPDFReader

from deepbrief.services import get_object, store_bytes

logger = logging.getLogger(__name__)


def _resolve_pdf_path(file_path: str | None, storage_key: str | None) -> tuple[str, Path | None]:
    """Return a local path to the PDF, downloading from shared storage if needed."""
    tmp_path: Path | None = None
    if storage_key:
        logger.info("read_pdf: fetching from shared storage: %s", storage_key)
        pdf_bytes = get_object(storage_key)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)
        file_path = str(tmp_path)

    if not file_path:
        raise ValueError("file_path is required when storage_key is not provided.")

    return file_path, tmp_path


def _persist_markdown_page(
    doc_folder: str,
    page_number: int,
    content_md: str,
    markdowns_directory: Path,
    storage_prefix: str,
    persist_locally: bool,
) -> dict[str, str | None]:
    """Persist a simple markdown page locally/in storage and return the paths."""
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


def read_pdf(ctx: WorkflowActivityContext, input_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Reads the PDF specified by `file_path` or `storage_key` and emits one entry per page.
    """
    input_data = input_data or {}
    file_path: str | None = input_data.get("file_path")
    storage_key: str | None = input_data.get("storage_key")
    doc_id: str | None = input_data.get("doc_id")
    markdowns_directory = Path(input_data.get("markdowns_directory", "output/markdowns"))
    storage_prefix = input_data.get("storage_prefix", "markdowns")
    persist_locally = bool(input_data.get("persist_locally", True))

    if not file_path and not storage_key:
        raise ValueError("Either file_path or storage_key must be provided.")

    local_path, tmp_path = _resolve_pdf_path(file_path, storage_key)

    records: list[dict[str, Any]] = []
    try:
        reader = PyPDFReader()
        chunks = reader.load(Path(local_path))
        logger.info("read_pdf: extracted %s chunks from %s", len(chunks), local_path)

        doc_folder = str(doc_id or Path(local_path).stem)
        base_metadata = {
            "document_id": doc_folder,
            "source": local_path,
            "storage_key": storage_key,
            "markdowns_directory": str(markdowns_directory),
            "markdowns_storage_prefix": storage_prefix,
        }

        for index, chunk in enumerate(chunks):
            data = chunk.model_dump()
            text = str(data.get("text", "")).strip()
            markdown_text = text or f"(Page {index} contained no extractable text.)"
            persisted = _persist_markdown_page(
                doc_folder=doc_folder,
                page_number=index,
                content_md=markdown_text,
                markdowns_directory=markdowns_directory,
                storage_prefix=storage_prefix,
                persist_locally=persist_locally,
            )
            page_metadata = {
                "page_number": index,
                "page_markdown_path": persisted["file_path"],
                "page_markdown_storage_key": persisted["storage_key"],
                "plain_text": text,
            }
            records.append({"text": markdown_text, "metadata": {**base_metadata, **page_metadata}})

        if not records:
            fallback_text = "(No text extracted from document.)"
            persisted = _persist_markdown_page(
                doc_folder=doc_folder,
                page_number=0,
                content_md=fallback_text,
                markdowns_directory=markdowns_directory,
                storage_prefix=storage_prefix,
                persist_locally=persist_locally,
            )
            records.append(
                {
                    "text": fallback_text,
                    "metadata": {
                        **base_metadata,
                        "page_number": 0,
                        "page_markdown_path": persisted["file_path"],
                        "page_markdown_storage_key": persisted["storage_key"],
                        "plain_text": fallback_text,
                    },
                }
            )

    except Exception as exc:
        logger.error("Failed to read file %s: %s", local_path, exc)
        raise
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return records
