import logging
import os

from dapr_agents import OpenAIChatClient
from dapr_agents.workflow.decorators import llm_activity
from dotenv import load_dotenv

from deepbrief.activities.models import PodcastDialogue, PodcastEpisode
from deepbrief.activities.prompt import GENERATE_EPISODE_PROMPT, GENERATE_TRANSCRIPT_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

# Initializing LLM clients with centralized configuration
llm = OpenAIChatClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_API_MODEL"),
    base_url=os.getenv("OPENAI_API_BASE_URL"),
)


@llm_activity(prompt=GENERATE_TRANSCRIPT_PROMPT, llm=llm)
def generate_transcript(
    podcast_name: str,
    host_name: str,
    prompt: str,
    max_rounds: int,
) -> PodcastDialogue:
    pass


@llm_activity(prompt=GENERATE_EPISODE_PROMPT, llm=llm)
def generate_episode_metadata(transcript: str, paper_id: str) -> PodcastEpisode:
    pass
