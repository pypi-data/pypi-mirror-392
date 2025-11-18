import logging
from typing import Any

from dapr.ext.workflow import DaprWorkflowContext

from deepbrief.activities.llm import generate_transcript
from deepbrief.activities.podcast import write_transcript_to_file
from deepbrief.activities.prompt import generate_prompt
from deepbrief.activities.readv2 import read_pdf_v2

logger = logging.getLogger(__name__)


def generate_transcripts_workflow(ctx: DaprWorkflowContext, input: dict):
    """
    Orchestrator that generates transcripts for a list of papers.
    """
    papers_metadata = input.get("papers_metadata") or []
    participants = input.get("participants") or []
    podcast_name = input.get("podcast_name", "DeepBrief Podcast")
    host_name = input.get("host_name", "Roberto Rodriguez")
    dialogue_max_rounds = int(input.get("dialogue_max_rounds", 3))
    transcripts_directory = input.get("transcripts_directory", "output/transcripts")
    transcripts_storage_prefix = input.get("transcripts_storage_prefix", "transcripts")
    persist_transcripts_locally = bool(input.get("persist_transcripts_locally", False))
    markdowns_directory = input.get("markdowns_directory", "output/markdowns")
    markdowns_storage_prefix = input.get("markdowns_storage_prefix", "markdowns")
    persist_markdowns_locally = bool(input.get("persist_markdowns_locally", False))

    transcripts_metadata: list[dict[str, Any]] = []

    for record in papers_metadata:
        canonical_id = record.get("id")
        latest_id = record.get("latest_id") or canonical_id
        file_path = record.get("file_path")
        storage_key = record.get("storage_key")
        if not storage_key and not file_path:
            continue

        # 1.1 - Read PDF Papers
        documents: list[dict[str, Any]] = yield ctx.call_activity(
            read_pdf_v2,
            input={
                "file_path": file_path,
                "storage_key": storage_key,
                "doc_id": latest_id,
                "markdowns_directory": markdowns_directory,
                "storage_prefix": markdowns_storage_prefix,
                "persist_locally": persist_markdowns_locally,
            },
        )
        if not documents:
            logger.warning(
                "No pages returned for %s; skipping transcripts.",
                latest_id,
            )
            continue

        # 1.2 - Prepare to process the documents
        accumulated_context = ""
        transcript_parts = []
        total_iterations = len(documents)

        for chunk_index, document in enumerate(documents):
            # Define the iteration index
            iteration_index = chunk_index + 1
            doc_text = document.get("text") or ""
            # Initialize the document_with_context with common fields
            document_with_context = {
                "text": str(doc_text).encode("utf-8", "replace").decode("utf-8"),
                "iteration_index": iteration_index,
                "total_iterations": total_iterations,
                "context": accumulated_context.encode("utf-8", "replace").decode("utf-8"),
                "participants": (
                    [p["name"] for p in participants if "name" in p]
                    if participants
                    else []
                ),
            }
            # Add doc_metadata for the first interaction
            if iteration_index == 1:
                document_with_context["doc_metadata"] = {
                    "title": str(record.get("title", "Unknown Title"))
                    .encode("utf-8", "replace")
                    .decode("utf-8"),
                    "summary": str(record.get("summary", "No summary available."))
                    .encode("utf-8", "replace")
                    .decode("utf-8"),
                }
            # 1.3: Generate the intermediate prompt
            generated_prompt = yield ctx.call_activity(
                generate_prompt, input=document_with_context
            )
            # 1.4: Generate the structured dialogue
            prompt_parameters = {
                "podcast_name": podcast_name,
                "host_name": host_name,
                "prompt": generated_prompt,
                "max_rounds": dialogue_max_rounds,
            }
            dialogue_entry = yield ctx.call_activity(generate_transcript, input=prompt_parameters)
            # Update context and transcript parts
            conversations = dialogue_entry["participants"]
            # Reset accumulated_context to only hold the latest conversation
            accumulated_context = ""
            for participant in conversations:
                accumulated_context += f" {participant['name']}: {participant['text']}"
                transcript_parts.append(participant)

        # 6.5: Write dialogue to a file
        transcript_result = yield ctx.call_activity(
            write_transcript_to_file,
            input={
                "podcast_dialogue": transcript_parts,
                "transcripts_directory": transcripts_directory,
                "file_name": f"{latest_id}.json",
                "storage_prefix": transcripts_storage_prefix,
                "persist_locally": persist_transcripts_locally,
            },
        )
        transcripts_metadata.append(
            {
                "article_id": latest_id,
                "file_path": transcript_result["file_path"],
                "storage_key": transcript_result["storage_key"],
                "markdowns_directory": markdowns_directory,
                "markdowns_storage_prefix": markdowns_storage_prefix,
            }
        )

    return {
        "transcripts_metadata": transcripts_metadata
    }
