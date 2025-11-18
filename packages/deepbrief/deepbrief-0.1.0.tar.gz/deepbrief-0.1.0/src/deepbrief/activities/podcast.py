import json
import logging
from pathlib import Path
from typing import Any

from dapr.ext.workflow import WorkflowActivityContext

from deepbrief.services import store_json

logger = logging.getLogger(__name__)


def write_transcript_to_file(ctx: WorkflowActivityContext, input_data: dict) -> dict[str, str]:
    """
    Write the structured podcast dialogue to a specified file in a given directory.

    """
    try:
        input_data = input_data or {}
        podcast_dialogue: dict[str, Any] = input_data.get("podcast_dialogue") or {}
        transcripts_directory: str = input_data.get("transcripts_directory", "output/transcripts")
        file_name: str = input_data.get("file_name", "transcript.json")
        storage_prefix: str = input_data.get("storage_prefix", "transcripts")
        persist_locally = bool(input_data.get("persist_locally", False))

        file_path = None
        if persist_locally:
            Path(transcripts_directory).mkdir(parents=True, exist_ok=True)
            file_path_obj = Path(transcripts_directory) / file_name
            with file_path_obj.open("w", encoding="utf-8") as file:
                json.dump(podcast_dialogue, file, ensure_ascii=False, indent=4)
            file_path = str(file_path_obj)
            logger.info("Podcast dialogue successfully written to %s", file_path)

        storage_key = f"{storage_prefix}/{file_name}"
        store_json(storage_key, podcast_dialogue)
        logger.info("Transcript uploaded to shared storage at %s", storage_key)

        return {"file_path": file_path, "storage_key": storage_key}
    except Exception as e:
        logger.error(f"Error writing podcast dialogue to file: {e}")
        raise


def write_episode_to_file(ctx: WorkflowActivityContext, input_data: dict):
    """
    Process the results and update the article index with podcast episode metadata.

    """
    input_data = input_data or {}
    article_index: dict[str, Any] = input_data.get("article_index") or {}
    results: list[dict[str, Any]] = input_data.get("results") or []
    episodes_directory: str = input_data.get("episodes_directory", "output/episodes")
    episodes_storage_prefix: str = input_data.get("episodes_storage_prefix", "episodes")
    persist_locally = bool(input_data.get("persist_locally", True))
    recordings_metadata = input_data.get("recordings_metadata") or []

    recordings_lookup = {
        rec.get("article_id"): rec for rec in recordings_metadata if rec.get("article_id")
    }

    outputs = []
    for result in results:
        paper_id = result["paper_id"]
        article_metadata = article_index.get(paper_id)
        if not article_metadata:
            continue

        episode_metadata = {
            "title": result["title"],
            "overview": result["overview"],
            "key_takeaways": result["key_takeaways"],
        }
        recording_entry = recordings_lookup.get(paper_id, {})

        envelope = {
            **article_metadata,
            "podcast_episode": episode_metadata,
            "recording_metadata": recording_entry,
        }

        file_path = None
        if persist_locally:
            Path(episodes_directory).mkdir(parents=True, exist_ok=True)
            output_file = Path(episodes_directory) / f"{paper_id}.json"
            output_file.write_text(json.dumps(envelope, indent=4), encoding="utf-8")
            file_path = str(output_file)

        storage_key = f"{episodes_storage_prefix}/{paper_id}.json"
        store_json(storage_key, envelope)
        logger.info("Saved episode metadata for %s (local=%s)", paper_id, bool(file_path))
        outputs.append({"file_path": file_path, "storage_key": storage_key})
    return outputs
