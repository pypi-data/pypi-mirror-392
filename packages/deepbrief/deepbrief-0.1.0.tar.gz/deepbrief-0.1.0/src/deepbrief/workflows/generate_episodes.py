import json
import logging
from pathlib import Path

import dapr.ext.workflow as wf
from dapr.ext.workflow import DaprWorkflowContext

from deepbrief.activities.llm import generate_episode_metadata
from deepbrief.activities.podcast import write_episode_to_file

logger = logging.getLogger(__name__)


def generate_episodes_workflow(ctx: DaprWorkflowContext, input: dict):
    """
    Orchestrator that generates podcast episode overviews from transcripts.
    """
    transcripts_metadata = input.get("transcripts_metadata") or []
    episode_summary_batch_size = int(input.get("episode_summary_batch_size", 3))
    episodes_directory = input.get("episodes_directory", "output/episodes")
    episodes_storage_prefix = input.get("episodes_storage_prefix", "episodes")
    persist_episodes_locally = bool(input.get("persist_episodes_locally", True))
    recordings_metadata = input.get("recordings_metadata") or []
    papers_metadata = input.get("papers_metadata") or []

    papers_metadata_lookup = {
        rec.get("latest_id"): rec
        for rec in papers_metadata
        if rec.get("latest_id")
    }

    total_overview_batches = (
        (len(transcripts_metadata) + episode_summary_batch_size - 1)
        // episode_summary_batch_size
        or 1
    )
    logger.info("Generating overviews for podcast episodes.")

    # Step 9: Create batches of transcript files
    for batch_start in range(0, len(transcripts_metadata), episode_summary_batch_size):
        current_batch = transcripts_metadata[batch_start : batch_start + episode_summary_batch_size]

        # Log the batch progress
        logger.info(
            "Processing overview batch %s of %s",
            batch_start // episode_summary_batch_size + 1,
            total_overview_batches,
        )

        # Fan-out: Create parallel tasks for the current batch of transcript files
        overview_generation_tasks = []
        for transcript_record in current_batch:
            # Read the JSON file
            with open(transcript_record["file_path"], encoding="utf-8") as file:
                transcript_parts = json.load(file)

            # Combine all text lines from the JSON file
            combined_text = ""  # Reset for each file
            for part in transcript_parts:
                combined_text += part["text"] + " "

            # Create a task for generating the episode overview
            paper_id = Path(transcript_record["file_path"]).stem
            overview_generation_tasks.append(
                ctx.call_activity(
                    generate_episode_metadata,
                    input={"transcript": combined_text, "paper_id": paper_id}
                )
            )

        # Fan-in: Wait for all overview generation tasks to complete
        results = yield wf.when_all(overview_generation_tasks)

        # Create episosed files
        outputs = yield ctx.call_activity(
            write_episode_to_file,
            input={
                "article_index": papers_metadata_lookup,
                "results": results,
                "episodes_directory": episodes_directory,
                "episodes_storage_prefix": episodes_storage_prefix,
                "persist_locally": persist_episodes_locally,
                "recordings_metadata": recordings_metadata,
            },
        )
        logger.info(
            "Overview batch %s completed successfully.",
            batch_start // episode_summary_batch_size + 1,
        )

    logger.info("All podcast episode overviews have been successfully generated.")
    return {"episodes_metadata": outputs or []}
