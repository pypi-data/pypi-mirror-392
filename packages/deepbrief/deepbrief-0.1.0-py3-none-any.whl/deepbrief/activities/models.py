from pydantic import BaseModel, Field


class PaperClassification(BaseModel):
    """Classification output for a paper."""

    relevant: bool = Field(
        ...,
        description="True if the paper should be retained for downstream processing.",
    )
    reason: str = Field(
        ...,
        description="Concise justification describing why the paper was (or was not) relevant.",
    )


class SpeakerEntry(BaseModel):
    """
    A model representing an individual speaker's contribution in a podcast dialogue.
    """

    name: str = Field(..., description="The name of the speaker participating in the dialogue.")
    text: str = Field(..., description="The text spoken by the speaker.")


class PodcastDialogue(BaseModel):
    """
    A model representing the structure of a podcast dialogue.
    """

    participants: list[SpeakerEntry] = Field(
        ...,
        description=(
            "Dialogue entries that capture each speaker's name and spoken text."
        ),
    )


class PodcastEpisode(BaseModel):
    """
    A model representing the structure of a podcast episode.
    """

    paper_id: str = Field(..., description="Identifier for the paper tied to this episode.")
    title: str = Field(
        ...,
        description="Engaging episode title that does not directly copy the paper title.",
    )
    overview: str = Field(
        ...,
        description="Short summary (3-4 sentences) highlighting the main discussion points.",
    )
    key_takeaways: list[str] = Field(
        ...,
        description="Up to five takeaways; each 1-2 sentences summarizing major insights.",
    )
