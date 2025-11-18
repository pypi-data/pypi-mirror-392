from typing import Any

from pydantic import BaseModel, Field


class ParticipantInput(BaseModel):
    name: str
    voice: str | None = None


class WorkflowStartResponse(BaseModel):
    instance_id: str
    submitted_input: dict[str, Any]


class WorkflowTerminateRequest(BaseModel):
    output: Any | None = None
    recursive: bool = True


class HostConfig(BaseModel):
    name: str
    voice: str | None = None


class PodcastWorkflowInput(BaseModel):
    class Config:
        validate_by_name = True

    podcast_name: str = Field(
        ...,
        description="Display name for the podcast episode series.",
    )
    host: HostConfig = Field(
        ...,
        description="Configuration for the host voice and name.",
    )
    participants: list[ParticipantInput] = Field(
        default_factory=list,
        description="List of participant configurations.",
    )
    dialogue_max_rounds: int = Field(
        default=3,
        ge=1,
        alias="max_rounds",
        description="Maximum dialogue rounds for transcript generation.",
    )
    output_directory: str = Field(
        default="output",
        description="Root directory for workflow artifacts.",
    )
    audio_model: str = Field(
        default="eleven_flash_v2_5",
        description="Voice model used for TTS.",
    )

    search_days: int = Field(
        default=30,
        ge=1,
        description="Lookback window for paper search.",
    )
    search_max_results: int = Field(
        default=5,
        ge=1,
        description="Max results per query when searching papers.",
    )
    classify_batch_size: int = Field(
        default=25,
        ge=1,
        description="Parallelism for LLM classification.",
    )
    download_batch_size: int = Field(
        default=5,
        ge=1,
        description="Parallelism for PDF downloads.",
    )
    transcript_creation_batch_size: int = Field(
        default=5,
        ge=1,
        description="Parallelism for transcript -> audio generation.",
    )
    episode_summary_batch_size: int = Field(
        default=3,
        ge=1,
        description="Parallelism for episode overview generation.",
    )

    papers_storage_prefix: str = Field(
        default="papers",
        description="Prefix used when uploading PDFs to shared storage.",
    )
    download_timeout_seconds: int = Field(
        default=60,
        ge=1,
        description="Timeout (seconds) for downloading PDFs from arXiv.",
    )
    persist_papers_locally: bool = Field(
        default=False,
        description="Persist downloaded PDFs to disk.",
    )
    indexes_storage_prefix: str = Field(
        default="indexes",
        description="Prefix used when uploading index artifacts to storage.",
    )
    persist_index_locally: bool = Field(
        default=False,
        description="Persist article index & metrics locally.",
    )
    transcripts_storage_prefix: str = Field(
        default="transcripts",
        description="Prefix used when uploading transcripts.",
    )
    persist_transcripts_locally: bool = Field(
        default=False,
        description="Persist generated transcripts locally.",
    )
    recordings_storage_prefix: str = Field(
        default="recordings",
        description="Prefix used when uploading audio recordings.",
    )
    persist_recordings_locally: bool = Field(
        default=False,
        description="Persist generated audio recordings locally.",
    )
    episodes_storage_prefix: str = Field(
        default="episodes",
        description="Prefix used when uploading episode files.",
    )
    persist_episodes_locally: bool = Field(
        default=False,
        description="Persist generated episode files locally.",
    )
    markdowns_storage_prefix: str = Field(
        default="markdowns",
        description="Prefix used when uploading markdown files.",
    )
    persist_markdowns_locally: bool = Field(
        default=False,
        description="Persist generated markdown files locally.",
    )
