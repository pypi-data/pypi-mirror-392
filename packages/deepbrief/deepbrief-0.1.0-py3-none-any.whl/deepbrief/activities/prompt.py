# ruff: noqa: E501
import logging
import textwrap

from dapr.ext.workflow import WorkflowActivityContext

logger = logging.getLogger(__name__)


def generate_prompt(ctx: WorkflowActivityContext, input_data: dict) -> str:
    """
    Generate a prompt dynamically for the chunk.
    """
    input_data = input_data or {}
    text = str(input_data.get("text", ""))
    iteration_index = int(input_data.get("iteration_index", 1))
    total_iterations = int(input_data.get("total_iterations", 1))
    context = str(input_data.get("context", ""))
    participants: list[str] = input_data.get("participants") or []
    doc_metadata = input_data.get("doc_metadata") or {}

    logger.info(f"Processing iteration {iteration_index} of {total_iterations}.")
    instructions = textwrap.dedent(f"""
    ## CONTEXT
    - Previous conversation: {context.strip() or "No prior context available."}
    - This is iteration {iteration_index} of {total_iterations}.
    """).strip()

    if participants:
        participant_names = ', '.join(participants)
        instructions += f"\n## PARTICIPANTS: {participant_names}"
    else:
        instructions += "\n## PARTICIPANTS: None (HOST-ONLY Conversation)"

    if iteration_index == 1:
        instructions += textwrap.dedent(
            f"""
            ## INSTRUCTIONS:
            - Start with a warm welcome to the podcast.
            - Introduce the host and any participants (never highlight missing participants).
            - Mention the paper title you are discussing (you are not the author):
              {doc_metadata.get('title', 'Unknown Title')}.
            - Summarize the planned discussion using the paper summary:
              {doc_metadata.get('summary', 'No summary available.')}.
            - Highlight why this paper matters and set an engaging tone.
            """
        ).strip()
    elif iteration_index == total_iterations:
        instructions += textwrap.dedent(
            """
            ## INSTRUCTIONS:
            - Conclude with a concise summary of the discussion.
            - Avoid phrases that imply restarting (e.g., "Welcome back" or "As we return").
            - Include farewells from the host and any participants.
            - Reflect on the key takeaways from the paper and the episode.
            """
        ).strip()
    else:
        instructions += textwrap.dedent(
            """
            ## INSTRUCTIONS:
            - Continue seamlessly without re-introducing the show.
            - Avoid phrases that suggest a restart (e.g., "Welcome back").
            - Build directly from the previous discussion and transition naturally.
            - Maintain continuity using the provided context.
            """
        ).strip()

    instructions += textwrap.dedent("""
    - Use the provided TEXT and CONTEXT as the basis for this segment. Let TEXT drive the
      discussion while CONTEXT maintains continuity.
    - Refer to CONTEXT when needed to connect prior discussion points.
    - Alternate between speakers (if available) to keep the conversation dynamic.
    - Keep responses concise, relevant, and focused on the current idea.
    - Transition smoothly between topics and maintain logical progression.
    - Elaborate on key points without repeating earlier content.
    - Use natural, conversational language.
    - When TEXT contains image descriptions or figure notes, reference what the visual shows
      and why it matters, keeping commentary brief.
    """).strip()
    return f"{instructions}\n## TEXT:\n{text.strip()}"


ANALYZE_PAPERS_PROMPT = """
# Instructions
You will receive JSON objects describing research papers. Each object includes:
- **id**: unique identifier
- **title**: paper title
- **summary**: abstract text

## Tasks
- Decide if the work applies GenAI/agentic systems to cybersecurity operations.
- Highlight papers where advanced AI meaningfully assists defenders or empowers attackers.

### Primary Focus
- Offensive strategies: AI-assisted pentesting, attack simulation, adversarial tactics.
- Defensive strategies: detection engineering, incident response, vulnerability assessment.

### Use Cases
- Explain how the AI approach helps security analysts mitigate threats, or how threat actors
  could weaponize it.

### Exclusion Criteria
- Skip generic AI topics without a concrete security-ops connection.
- Skip broad privacy / governance / ethics discussions without agent/LLM security content.

## Research Papers
{general_papers}

## Output
- Return the ids of papers that satisfy the criteria above.
- Ensure your reasoning references the instructions.
"""

GENERATE_TRANSCRIPT_PROMPT = """
# PODCAST GENERATOR
- Generate a structured and engaging podcast dialogue based on the provided CONTEXT and TEXT.
- The podcast is titled '{podcast_name}' and is hosted by {host_name}.
- If participants are present, alternate naturally between the host and participants to ensure a dynamic and balanced conversational flow.
- Each participant (including the host) is limited to a maximum of {max_rounds} turns per iteration.
- A "round" consists of one turn by the host followed by one turn by a participant.
- If no participants are available, the host drives the conversation independently and should NOT mention the absence of other participants.
- Focus on maintaining a concise and coherent dialogue while progressively building upon the provided CONTEXT and TEXT.
- Ensure the conversation feels natural, engaging, and focused on the specified topics.
- Simplify complex concepts to make them accessible and relatable to a general audience.
- When image descriptions or figure notes appear in the TEXT, integrate them naturally (what the visual shows and why it matters) without over-explaining.
{prompt}
"""

GENERATE_EPISODE_PROMPT = """
# EPISODE OVERVIEW GENERATOR
You will be provided with the full transcript of a podcast episode discussing a specific research paper. Your task is to create the following:

1. **Engaging Episode Title**: Craft a concise and easy-to-read title that captures the main essence of the episode. The title should be engaging and accessible to a general audience. Do not copy the title of the research paper. Instead, summarize the central theme or focus in a way that piques curiosity.
2. **Episode Overview**: Write a 3-4 sentence summary of the episode. Focus on the main discussion points, the topics covered, and how they connect to the broader implications for cybersecurity, Generative AI, or AI agents. Make it informative yet easy to read.
3. **Key Takeaways**: Provide a concise list of up to **5 key insights** or takeaways from the episode. Each takeaway should be 1-2 sentences long and focus on:
   - The most important findings or points discussed in the paper.
   - How these findings relate to cybersecurity challenges or opportunities.
   - Broader implications for AI-driven defense or offensive strategies, emphasizing their practical relevance.

## Instructions
- Use clear and concise language. Avoid jargon or overly complex phrases.
- Ensure the tone remains professional but engaging.
- Structure each section logically and ensure the content flows smoothly.
- Highlight practical relevance and why the listener should care about these topics.

## Paper ID
{paper_id}

## Episode Transcript
{transcript}
"""
