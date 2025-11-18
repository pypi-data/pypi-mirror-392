import logging
from datetime import timedelta

import dapr.ext.workflow as wf
from dapr.ext.workflow import DaprWorkflowContext

from deepbrief.activities.classify import classify_papers
from deepbrief.activities.create_index import create_articles_index
from deepbrief.activities.download import download_paper
from deepbrief.activities.search import search_papers

logger = logging.getLogger(__name__)

# --- retry policy ONLY for LLM-based activities ---
CLASSIFY_RETRY_POLICY = wf.RetryPolicy(
    first_retry_interval=timedelta(seconds=1),   # initial backoff
    backoff_coefficient=2.0,                     # exponential
    max_retry_interval=timedelta(seconds=60),    # cap individual delay
    max_number_of_attempts=6,                    # total tries
    retry_timeout=timedelta(minutes=5),          # overall retry window
)


def get_papers_workflow(ctx: DaprWorkflowContext, input: dict):
    """
    Orchestrator that searches, classifies, and downloads research papers.
    """
    index_directory = input.get("index_directory", "output/index")
    papers_directory = input.get("papers_directory", "output/papers")
    days = int(input.get("days", 30))
    search_max_results = int(input.get("search_max_results", 5))
    classify_batch_size = max(
        1,
        int(input.get("classify_batch_size") or input.get("batch_size", 10)),
    )
    download_batch_size = max(1, int(input.get("download_batch_size", 5)))
    papers_storage_prefix = input.get("papers_storage_prefix", "papers")
    download_timeout_seconds = int(input.get("download_timeout_seconds", 60))
    persist_papers_locally = bool(input.get("persist_papers_locally", False))
    indexes_storage_prefix = input.get("indexes_storage_prefix", "indexes")
    persist_index_locally = bool(input.get("persist_index_locally", True))

    # 1) search papers
    res = yield ctx.call_activity(
        search_papers,
        input={"days": days, "max_results": search_max_results},
        retry_policy=CLASSIFY_RETRY_POLICY,
    )
    metrics = res["metrics"]
    articles = {rec["id"]: rec for rec in res.get("records", [])}

    # 2) LLM classify articles (fan-out with bounded parallelism)
    work = []
    for cid, rec in articles.items():
        work.append((cid, rec.get("title", ""), rec.get("summary", "")))

    # Process in batches
    total_batches = max(1, (len(work) + classify_batch_size - 1) // classify_batch_size)
    for bstart in range(0, len(work), classify_batch_size):
        bidx = bstart // classify_batch_size + 1
        batch = work[bstart:bstart + classify_batch_size]

        tasks = []
        for (_cid, title, abstract) in batch:
            tasks.append(
                ctx.call_activity(
                    classify_papers,
                    input={"title": title, "abstract": abstract},
                    retry_policy=CLASSIFY_RETRY_POLICY,
                )
            )

        results = yield wf.when_all(tasks)

        # Collect results
        for result, (cid, _, _) in zip(results, batch, strict=False):
            articles[cid]["classification"] = result or {}

        if not ctx.is_replaying:
            logger.info(
                "classify_papers: completed batch %s/%s (%s items, batch_size=%s)",
                bidx,
                total_batches,
            len(batch),
            classify_batch_size,
        )
    # 3) Download PDFs (fan-out batches)
    # Build download worklist based on classification
    download_work = [
        rec
        for rec in articles.values()
        if rec.get("classification", {}).get("relevant")
    ]
    # Process in batches
    total_download_batches = max(
        1,
        (len(download_work) + download_batch_size - 1) // download_batch_size,
    )
    for dstart in range(0, len(download_work), download_batch_size):
        batch = download_work[dstart : dstart + download_batch_size]
        tasks = []
        for rec in batch:
            latest_id = rec.get("latest_id")

            tasks.append(
                ctx.call_activity(
                    download_paper,
                    input={
                        "paper_id": rec["id"],
                        "latest_id": latest_id or rec["id"],
                        "title": rec.get("title", ""),
                        "papers_directory": papers_directory,
                        "storage_prefix": papers_storage_prefix,
                        "download_timeout_seconds": download_timeout_seconds,
                        "persist_locally": persist_papers_locally,
                    },
                )
            )

        results = yield wf.when_all(tasks)
        for result, rec in zip(results, batch, strict=False):
            if not result:
                continue
            rec["file_path"] = result.get("file_path")
            rec["storage_key"] = result.get("storage_key")

        if not ctx.is_replaying:
            logger.info(
                "download_paper: completed batch %s/%s (%s items)",
                (dstart // download_batch_size) + 1,
                total_download_batches,
                len(batch),
            )

    relevant_records = []
    for rec in articles.values():
        classification = rec.get("classification") or {}
        if not classification.get("relevant"):
            continue
        relevant_records.append(
            {
                "id": rec["id"],
                "latest_id": rec.get("latest_id"),
                "matched": rec.get("matched", []),
                "labels": rec.get("labels", []),
                "title": rec.get("title", ""),
                "summary": rec.get("summary", ""),
                "authors": rec.get("authors", []),
                "categories": rec.get("categories", []),
                "updated": rec.get("updated", ""),
                "file_path": rec.get("file_path", ""),
                "storage_key": rec.get("storage_key", ""),
                "reason": classification.get("reason", ""),
            }
        )

    index_artifacts = yield ctx.call_activity(
        create_articles_index,
        input={
            "papers_metadata": relevant_records,
            "metrics": metrics,
            "index_directory": index_directory,
            "storage_prefix": indexes_storage_prefix,
            "persist_locally": persist_index_locally,
        },
    )

    return {
        "papers_metadata": relevant_records,
        "index_artifacts": index_artifacts,
    }
