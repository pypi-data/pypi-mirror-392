import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dapr.ext.workflow import WorkflowActivityContext
from dapr_agents.document import ArxivFetcher

logger = logging.getLogger(__name__)


# Keep your broad category macro
CATS = (
    "cat:cs.AI OR cat:cs.LG OR cat:cs.CR OR cat:cs.MA OR cat:cs.CL OR "
    "cat:cs.SE OR cat:cs.DC OR cat:cs.NE OR cat:cs.DB OR cat:cs.DS"
)

# Require LLM/Agentic Context
LLM = (
    "\"large language model\" OR LLM OR \"GenAI\" OR \"generative AI\" OR "
    "RAG OR \"retrieval augmented generation\" OR \"retrieval-augmented\" OR "
    "agent OR agentic OR \"Agentic AI\" OR \"AI agent\" OR \"Agentic RAG\" OR "
    "\"autonomous agent\" OR \"multi-agent\""
)

# Compact, fielded candidates (ti/abs) per topic
CANDIDATES = {
    "Red": [
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"penetration testing\" OR abs:\"penetration testing\" OR abs:pentesting)"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:exploit OR abs:exploit OR ti:vulnerability OR abs:vulnerability)"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:malware OR abs:malware OR ti:C2 OR abs:C2)"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"red team\" OR abs:\"red team\" OR ti:\"red teaming\" OR abs:\"red teaming\")"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:phishing OR abs:phishing OR ti:\"social engineering\" "
            "OR abs:\"social engineering\")"
        ),
    ],
    "Blue": [
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"security operations\" OR abs:\"security operations\" OR ti:SOC OR abs:SecOps)"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"intrusion detection\" OR abs:\"intrusion detection\")"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"threat detection\" OR abs:\"threat detection\")"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"threat hunting\" OR abs:\"threat hunting\")"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"threat intelligence\" OR abs:\"threat intelligence\" OR ti:CTI OR abs:CTI "
            "OR ti:\"indicator of compromise\" OR abs:\"indicator of compromise\" "
            "OR ti:IOC OR abs:IOC)"
        ),
        (
            f"({CATS}) AND (ti:({LLM}) OR abs:({LLM})) AND "
            "(ti:\"incident response\" OR abs:\"incident response\" OR ti:\"digital forensics\" "
            "OR abs:\"digital forensics\" OR ti:DFIR OR abs:DFIR)"
        ),
    ],
}


def _parse_updated(value: str) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        logger.debug("Unable to parse arXiv updated timestamp: %s", value)
        return None


def search_papers(ctx: WorkflowActivityContext, input_data: dict) -> dict:
    """
    Run all candidate queries with minute-granularity UTC window.

    Args:
        ctx: Workflow activity context.
        input_data: Dictionary with optional keys:
            - days: Lookback window in days (default: 30)
            - max_results: Max results per query (default: 5)
            - debug_dirpath: Optional directory path to dump debug index and metrics

    Returns:
        Dictionary with:
            - hits: Mapping of canonical paper IDs to details
            - metrics: Count of hits per candidate query
    """
    days = int((input_data or {}).get("days", 30))
    max_results = int((input_data or {}).get("max_results", 5))
    debug_dir = (input_data or {}).get("debug_dirpath")

    fetcher = ArxivFetcher()
    hi = datetime.now(timezone.utc)
    lo = hi - timedelta(days=days)
    logger.info(
        "search_candidates window: from %s to %s",
        lo.strftime("%Y%m%d%H%M"),
        hi.strftime("%Y%m%d%H%M"),
    )

    records = []
    record_map = {}
    metrics = {
        topic: {f"cand_{i + 1}": 0 for i in range(len(qs))}
        for topic, qs in CANDIDATES.items()
    }

    for topic, qs in CANDIDATES.items():
        for i, base_q in enumerate(qs, start=1):
            logger.info(
                "Executing %s cand_%s window [%s -> %s]",
                topic,
                i,
                lo.strftime("%Y%m%d%H%M"),
                hi.strftime("%Y%m%d%H%M"),
            )
            docs = fetcher.search(
                query=base_q,
                from_date=lo,
                to_date=hi,
                include_summary=True,
                max_results=max_results,
            )
            metrics[topic][f"cand_{i}"] += len(docs)
            for d in docs:
                entry_id = d.metadata["entry_id"]         # https://arxiv.org/abs/2501.01234v2
                vid = entry_id.split("/")[-1]             # 2501.01234v2
                cid = vid.split("v")[0]                   # 2501.01234

                updated_dt = _parse_updated(d.metadata.get("updated"))
                if updated_dt and not (lo <= updated_dt <= hi):
                    continue

                tag = f"{topic}:cand_{i}"

                existing = record_map.get(cid)
                if not existing:
                    metadata = {
                        "id": cid,
                        "latest_id": vid,
                        "matched": [tag],
                        "labels": [topic],
                        "title": d.metadata.get("title", ""),
                        "summary": d.metadata.get("summary", ""),
                        "authors": d.metadata.get("authors", []),
                        "categories": d.metadata.get("categories", []),
                        "updated": d.metadata.get("updated", ""),
                    }
                    records.append(metadata)
                    record_map[cid] = metadata
                else:
                    if tag not in existing["matched"]:
                        existing["matched"].append(tag)
                    if topic not in existing["labels"]:
                        existing["labels"].append(topic)

    for r in records:
        r["matched"].sort()
        r["labels"].sort()

    if debug_dir:
        dirpath = Path(debug_dir)
        dirpath.mkdir(parents=True, exist_ok=True)
        idx_path = dirpath / "article_index_debug.jsonl"
        metrics_path = dirpath / "metrics_debug.json"

        count = 0
        with idx_path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record))
                f.write("\n")
                count += 1

        with metrics_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        logger.info(
            "search_candidates debug dump: %s records written to %s",
            count,
            idx_path,
        )

    logger.info("search_candidates: %s unique canonical IDs", len(records))
    return {"records": records, "metrics": metrics}
