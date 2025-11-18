import json
from pathlib import Path
from typing import Any

from dapr.ext.workflow import WorkflowActivityContext

from deepbrief.services import store_bytes


def create_articles_index(
    ctx: WorkflowActivityContext,
    input_data: dict[str, Any],
) -> dict[str, str | None]:
    """Persist the curated articles index and metrics."""

    papers_metadata: list[dict[str, Any]] = input_data.get("papers_metadata") or []
    metrics = input_data.get("metrics") or {}
    index_directory = Path(input_data.get("index_directory", "output/index"))
    storage_prefix = input_data.get("storage_prefix", "indexes")
    persist_locally = bool(input_data.get("persist_locally", True))

    lines = [json.dumps(record) for record in papers_metadata]
    content = "\n".join(lines)
    if content and not content.endswith("\n"):
        content += "\n"
    index_bytes = content.encode("utf-8")
    metrics_bytes = json.dumps(metrics, indent=2).encode("utf-8")

    idx_path_str = None
    metrics_path_str = None

    if persist_locally:
        index_directory.mkdir(parents=True, exist_ok=True)
        idx_path = index_directory / "article_index_classified.jsonl"
        metrics_path = index_directory / "metrics.json"
        idx_path.write_text(content, encoding="utf-8")
        metrics_path.write_bytes(metrics_bytes)
        idx_path_str = str(idx_path)
        metrics_path_str = str(metrics_path)

    index_storage_key = f"{storage_prefix}/{index_directory.name}/article_index_classified.jsonl"
    metrics_storage_key = f"{storage_prefix}/{index_directory.name}/metrics.json"

    store_bytes(index_storage_key, index_bytes, metadata={"contentType": "application/json"})
    store_bytes(metrics_storage_key, metrics_bytes, metadata={"contentType": "application/json"})

    return {
        "index_path": idx_path_str,
        "metrics_path": metrics_path_str,
        "index_storage_key": index_storage_key,
        "metrics_storage_key": metrics_storage_key,
    }
