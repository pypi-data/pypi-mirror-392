import logging
from contextlib import asynccontextmanager

import dapr.ext.workflow as wf
from dapr.ext.workflow import DaprWorkflowClient
from fastapi import FastAPI, HTTPException

from deepbrief.activities.classify import classify_papers
from deepbrief.activities.create_index import create_articles_index
from deepbrief.activities.download import download_paper
from deepbrief.activities.llm import (
    generate_episode_metadata,
    generate_transcript,
)
from deepbrief.activities.podcast import write_episode_to_file, write_transcript_to_file
from deepbrief.activities.prompt import generate_prompt
from deepbrief.activities.read import read_pdf
from deepbrief.activities.readv2 import read_pdf_v2
from deepbrief.activities.search import search_papers
from deepbrief.activities.speak import convert_transcript_to_audio
from deepbrief.workflows.create_podcast import create_podcast_workflow
from deepbrief.workflows.generate_episodes import generate_episodes_workflow
from deepbrief.workflows.generate_recordings import generate_recordings_workflow
from deepbrief.workflows.generate_transcripts import generate_transcripts_workflow
from deepbrief.workflows.get_papers import get_papers_workflow
from deepbrief.workflows.models import (
    PodcastWorkflowInput,
    WorkflowStartResponse,
    WorkflowTerminateRequest,
)

logger = logging.getLogger(__name__)


runtime = wf.WorkflowRuntime()
runtime.register_workflow(create_podcast_workflow)
runtime.register_workflow(get_papers_workflow)
runtime.register_workflow(generate_transcripts_workflow)
runtime.register_workflow(generate_recordings_workflow)
runtime.register_workflow(generate_episodes_workflow)
runtime.register_activity(download_paper)
runtime.register_activity(read_pdf)
runtime.register_activity(read_pdf_v2)
runtime.register_activity(generate_prompt)
runtime.register_activity(generate_transcript)
runtime.register_activity(convert_transcript_to_audio)
runtime.register_activity(write_transcript_to_file)
runtime.register_activity(write_episode_to_file)
runtime.register_activity(generate_episode_metadata)
runtime.register_activity(create_articles_index)
runtime.register_activity(classify_papers)
runtime.register_activity(search_papers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime.start()
    logger.info("Workflow runtime started.")
    try:
        yield
    finally:
        runtime.shutdown()
        logger.info("Workflow runtime stopped.")


app = FastAPI(
    title="Document to Podcast Workflow",
    description="FastAPI wrapper around the create_podcast_workflow workflow.",
    version="0.1.0",
    lifespan=lifespan,
)


def _format_state_payload(state):
    payload = state.to_json()
    for ts_field in ("created_at", "last_updated_at"):
        if payload.get(ts_field):
            payload[ts_field] = payload[ts_field].isoformat()
    return payload


@app.post("/workflows/research-podcast", response_model=WorkflowStartResponse)
def start_workflow(request: PodcastWorkflowInput) -> WorkflowStartResponse:
    client = DaprWorkflowClient()
    payload = request.model_dump()
    instance_id = client.schedule_new_workflow(
        workflow=create_podcast_workflow,
        input=payload,
    )
    logger.info("Started workflow %s", instance_id)
    return WorkflowStartResponse(instance_id=instance_id, submitted_input=payload)


@app.get("/workflows/{instance_id}")
def get_workflow_state(instance_id: str, fetch_payloads: bool = True):
    client = DaprWorkflowClient()
    state = client.get_workflow_state(instance_id, fetch_payloads=fetch_payloads)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _format_state_payload(state)


@app.get("/workflows/{instance_id}/wait")
def wait_for_completion(instance_id: str, timeout: int = 1800):
    client = DaprWorkflowClient()
    state = client.wait_for_workflow_completion(instance_id, timeout_in_seconds=timeout)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    payload = _format_state_payload(state)
    if state.runtime_status.name == "COMPLETED":
        logger.info("Workflow %s completed", instance_id)
    else:
        logger.error("Workflow %s ended with status %s", instance_id, state.runtime_status)
        if state.failure_details:
            payload["failure_details"] = {
                "message": state.failure_details.message,
                "error_type": state.failure_details.error_type,
                "stack_trace": state.failure_details.stack_trace,
            }
    return payload


@app.post("/workflows/{instance_id}/terminate")
def terminate_workflow(instance_id: str, request: WorkflowTerminateRequest):
    client = DaprWorkflowClient()
    client.terminate_workflow(
        instance_id,
        output=request.output,
        recursive=request.recursive,
    )
    logger.info("Terminated workflow %s", instance_id)
    return {"instance_id": instance_id, "status": "TERMINATED"}
