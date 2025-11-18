import logging
from pathlib import Path
from typing import Any

from dapr.ext.workflow import DaprWorkflowContext

from deepbrief.workflows.generate_episodes import generate_episodes_workflow
from deepbrief.workflows.generate_recordings import generate_recordings_workflow
from deepbrief.workflows.generate_transcripts import generate_transcripts_workflow
from deepbrief.workflows.get_papers import get_papers_workflow
from deepbrief.workflows.models import PodcastWorkflowInput

logger = logging.getLogger(__name__)


def create_podcast_workflow(ctx: DaprWorkflowContext, input: dict[str, Any]):
    """Main orchestrator that researches papers and turns them into podcast assets."""
    config = PodcastWorkflowInput(**input)

    podcast_name = config.podcast_name
    host_config = config.host.model_dump()
    participants_config = [p.model_dump() for p in config.participants]
    dialogue_max_rounds = config.dialogue_max_rounds
    output_directory = config.output_directory
    index_directory = str(Path(output_directory) / "index")
    papers_directory = str(Path(output_directory) / "papers")
    transcripts_directory = str(Path(output_directory) / "transcripts")
    markdowns_directory = str(Path(output_directory) / "markdowns")
    recordings_directory = str(Path(output_directory) / "recordings")
    episodes_directory = str(Path(output_directory) / "episodes")
    audio_model = config.audio_model
    search_days = config.search_days
    search_max_results = config.search_max_results
    classify_batch_size = config.classify_batch_size
    download_batch_size = config.download_batch_size
    transcript_creation_batch_size = config.transcript_creation_batch_size
    episode_summary_batch_size = config.episode_summary_batch_size
    papers_storage_prefix = config.papers_storage_prefix
    download_timeout_seconds = config.download_timeout_seconds
    persist_papers_locally = config.persist_papers_locally
    indexes_storage_prefix = config.indexes_storage_prefix
    persist_index_locally = config.persist_index_locally
    transcripts_storage_prefix = config.transcripts_storage_prefix
    persist_transcripts_locally = config.persist_transcripts_locally
    recordings_storage_prefix = config.recordings_storage_prefix
    persist_recordings_locally = config.persist_recordings_locally
    episodes_storage_prefix = config.episodes_storage_prefix
    persist_episodes_locally = config.persist_episodes_locally
    markdowns_storage_prefix = config.markdowns_storage_prefix
    persist_markdowns_locally = config.persist_markdowns_locally

    # Step 1: search + classify + download papers
    papers_results = yield ctx.call_child_workflow(
        get_papers_workflow,
        input={
            "days": search_days,
            "search_max_results": search_max_results,
            "classify_batch_size": classify_batch_size,
            "download_batch_size": download_batch_size,
            "download_timeout_seconds": download_timeout_seconds,
            "indexes_storage_prefix": indexes_storage_prefix,
            "persist_index_locally": persist_index_locally,
            "index_directory": index_directory,
            "papers_storage_prefix": papers_storage_prefix,
            "persist_papers_locally": persist_papers_locally,
            "papers_directory": papers_directory,
        },
    )

    papers_metadata = papers_results.get("papers_metadata") or []
    if not papers_metadata:
        logger.info("No relevant papers found with downloaded PDFs; exiting workflow.")
        return

    # Step 2: Generate transcripts for each paper
    transcripts_results = yield ctx.call_child_workflow(
        generate_transcripts_workflow,
        input={
            "papers_metadata": [papers_metadata[0]],
            "participants": participants_config,
            "podcast_name": podcast_name,
            "host_name": host_config.get("name", "Host"),
            "dialogue_max_rounds": dialogue_max_rounds,
            "transcripts_storage_prefix": transcripts_storage_prefix,
            "persist_transcripts_locally": persist_transcripts_locally,
            "transcripts_directory": transcripts_directory,
            "markdowns_storage_prefix": markdowns_storage_prefix,
            "persist_markdowns_locally": persist_markdowns_locally,
            "markdowns_directory": markdowns_directory,
        },
    )
    transcripts_metadata = transcripts_results.get("transcripts_metadata") or []
    if not transcripts_metadata:
        logger.info("No transcripts generated; skipping audio and episode steps.")
        return

    # Step 3: Convert transcripts to audio via child workflow
    recordings_results = yield ctx.call_child_workflow(
        generate_recordings_workflow,
        input={
            "transcripts_metadata": transcripts_metadata,
            "transcript_creation_batch_size": transcript_creation_batch_size,
            "host_config": host_config,
            "participants_config": participants_config,
            "audio_model": audio_model,
            "recordings_storage_prefix": recordings_storage_prefix,
            "persist_recordings_locally": persist_recordings_locally,
            "recordings_directory": recordings_directory,
        },
    )
    recordings_metadata = recordings_results.get("recordings_metadata") or []
    if not recordings_metadata:
        logger.warning("No recordings metadata returned; continuing with episode generation.")

    # Step 4: Generate episode overviews + files via child workflow
    episodes_results = yield ctx.call_child_workflow(
        generate_episodes_workflow,
        input={
            "transcripts_metadata": transcripts_metadata,
            "episode_summary_batch_size": episode_summary_batch_size,
            "episodes_directory": episodes_directory,
            "papers_metadata": papers_metadata,
            "episodes_storage_prefix": episodes_storage_prefix,
            "persist_episodes_locally": persist_episodes_locally,
            "recordings_metadata": recordings_metadata,
        },
    )
    episodes_metadata = episodes_results.get("episodes_metadata") or []
    return {
        "papers_metadata": papers_metadata,
        "transcripts_metadata": transcripts_metadata,
        "recordings_metadata": recordings_metadata,
        "episodes_metadata": episodes_metadata,
    }
