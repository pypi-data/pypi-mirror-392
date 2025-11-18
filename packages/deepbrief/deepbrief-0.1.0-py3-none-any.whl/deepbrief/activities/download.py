import logging
from pathlib import Path
from typing import Any

import arxiv
import requests
from dapr.ext.workflow import WorkflowActivityContext

from deepbrief.services import store_bytes

logger = logging.getLogger(__name__)


def _fetch_result_by_id(content_id: str) -> arxiv.Result | None:
    """Fetch a single arXiv result without downloading the PDF."""
    search = arxiv.Search(id_list=[content_id])
    client = arxiv.Client()
    try:
        return next(client.results(search=search), None)
    except StopIteration:
        return None


def _download_pdf_bytes(result: arxiv.Result, timeout: int) -> bytes:
    """Download the PDF bytes for a given result using its pdf_url."""
    response = requests.get(result.pdf_url, timeout=timeout)
    response.raise_for_status()
    return response.content


def download_paper(ctx: WorkflowActivityContext, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Download a single paper (if needed) and upload it to shared storage.
    """
    data = input_data or {}
    paper_id = data.get("paper_id")
    latest_id = data.get("latest_id")
    title = data.get("title", paper_id or latest_id or "unknown paper")
    if not latest_id:
        raise ValueError("latest_id must be provided")

    persist_locally = bool(data.get("persist_locally"))
    papers_directory = Path(data.get("papers_directory", "output/papers"))
    if persist_locally:
        papers_directory.mkdir(parents=True, exist_ok=True)

    pdf_path: Path | None = None
    pdf_bytes: bytes | None = None

    logger.info("Downloading %s (%s)", title, latest_id)
    result = _fetch_result_by_id(latest_id)
    if not result:
        raise RuntimeError(f"Failed to fetch metadata for {latest_id}")

    if not title or title == "unknown paper":
        title = result.title

    try:
        timeout = int(data.get("download_timeout_seconds", 60))
        pdf_bytes = _download_pdf_bytes(result, timeout)
    except Exception as exc:
        raise RuntimeError(f"Failed to download PDF for {latest_id}: {exc}") from exc

    if persist_locally:
        filename = f"{result.get_short_id()}.pdf"
        pdf_path = papers_directory / filename
        pdf_path.write_bytes(pdf_bytes)

    storage_prefix = data.get("storage_prefix", "papers")
    filename = pdf_path.name if pdf_path else f"{latest_id}.pdf"
    storage_key = f"{storage_prefix}/{filename}"
    store_bytes(storage_key, pdf_bytes, metadata={"contentType": "application/pdf"})

    logger.info("Uploaded %s to shared storage at %s", latest_id, storage_key)

    canonical_id = paper_id or latest_id.split("v")[0]

    return {
        "paper_id": canonical_id,
        "latest_id": latest_id,
        "file_path": str(pdf_path) if pdf_path else None,
        "storage_key": storage_key,
        "title": title,
    }
