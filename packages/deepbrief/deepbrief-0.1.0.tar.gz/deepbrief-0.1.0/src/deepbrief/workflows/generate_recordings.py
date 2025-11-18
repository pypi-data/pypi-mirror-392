import json
import logging
from pathlib import Path
from typing import Any

import dapr.ext.workflow as wf
from dapr.ext.workflow import DaprWorkflowContext

from deepbrief.activities.speak import convert_transcript_to_audio
from deepbrief.services import get_object

logger = logging.getLogger(__name__)


def generate_recordings_workflow(ctx: DaprWorkflowContext, input: dict):
    """
    Orchestrator that generates audio recordings from transcripts.
    """
    transcripts_metadata = input.get("transcripts_metadata") or []
    transcript_creation_batch_size = int(input.get("transcript_creation_batch_size", 5))
    recordings_directory = input.get("recordings_directory", "output/recordings")
    host_config = input.get("host_config", {})
    participants_config = input.get("participants_config", {})
    audio_model = input.get("audio_model", "eleven_flash_v2_5")
    recordings_storage_prefix = input.get("recordings_storage_prefix", "recordings")
    persist_recordings_locally = bool(input.get("persist_recordings_locally", False))

    # Create batches of transcript files
    logger.info("Creating transcript files.")
    total_audio_batches = (
        (len(transcripts_metadata) + transcript_creation_batch_size - 1)
        // transcript_creation_batch_size
        or 1
    )
    recordings_metadata: list[dict[str, Any]] = []
    for batch_start in range(0, len(transcripts_metadata), transcript_creation_batch_size):
        current_batch = transcripts_metadata[
            batch_start : batch_start + transcript_creation_batch_size
        ]

        # Log the batch progress
        logger.info(
            "Processing audio batch %s of %s",
            batch_start // transcript_creation_batch_size + 1,
            total_audio_batches,
        )

        # Fan-out: Create parallel tasks for the current batch of transcript files
        audio_conversion_tasks = []
        for transcript_record in current_batch:
            transcript_parts = _load_transcript_parts(transcript_record)

            file_path = transcript_record.get("file_path")
            if file_path:
                file_name = Path(file_path).stem
            else:
                file_name = transcript_record.get("article_id") or "transcript"

            # Create a task for audio conversion
            audio_conversion_tasks.append(
                ctx.call_activity(
                    convert_transcript_to_audio,
                    input={
                        "transcript_parts": transcript_parts,
                        "recordings_directory": recordings_directory,
                        "file_name": file_name,
                        "host_config": host_config,
                        "participants_config": participants_config,
                        "model": audio_model,
                        "storage_prefix": recordings_storage_prefix,
                        "persiste_locally": persist_recordings_locally,
                    },
                )
            )

        # Fan-in: Wait for the current batch of audio conversion tasks to complete
        results = yield wf.when_all(audio_conversion_tasks)
        for transcript_record, audio_result in zip(
            current_batch,
            results,
            strict=False,
        ):
            if not audio_result:
                continue
            recordings_metadata.append(
                {
                    "article_id": transcript_record.get("article_id"),
                    "recording_file_path": audio_result.get("file_path"),
                    "recording_storage_key": audio_result.get("storage_key"),
                    "transcript_file_path": transcript_record.get("file_path"),
                    "transcript_storage_key": transcript_record.get("storage_key"),
                }
            )

        logger.info(
            "Audio batch %s completed successfully.",
            batch_start // transcript_creation_batch_size + 1,
        )

    logger.info("All audio files have been successfully generated.")
    return {"recordings_metadata": recordings_metadata}


def _load_transcript_parts(record: dict[str, Any]) -> list[dict[str, Any]]:
    file_path = record.get("file_path")
    if file_path:
        path = Path(file_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)

    storage_key = record.get("storage_key")
    if storage_key:
        data = get_object(storage_key)
        return json.loads(data.decode("utf-8"))

    raise RuntimeError("Transcript record missing both file_path and storage_key")
