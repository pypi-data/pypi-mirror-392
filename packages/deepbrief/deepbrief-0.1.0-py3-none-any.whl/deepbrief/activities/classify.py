import logging
import os

from dapr_agents import OpenAIChatClient
from dapr_agents.workflow.decorators import llm_activity
from dotenv import load_dotenv

from deepbrief.activities.models import PaperClassification

logger = logging.getLogger(__name__)

LLM_LABEL_PROMPT = """
# Role
You classify research papers focused on **LLM / agentic security**.

# Relevance Definition
A paper is relevant when it uses **LLMs, RAG, autonomous / agentic AI, or tool-using agents**
in a **security operations** context. Cover both attacking and defending AI systems.

## Offense (red teaming & attacking AI)
- Augmenting offensive security work with LLMs / agents.
- Research that targets AI systems (prompt injection, jailbreaks, adversarial examples, model
  extraction / poisoning, red-team frameworks, automated exploit discovery / evasion,
  social-engineering simulation, orchestration of offensive tools).

## Defense (blue teams & protecting AI)
- Using LLMs / agents for SOC, threat intel, detection engineering, IR, or threat hunting.
- Safeguarding AI systems in production (alert triage, query/log generation, enrichment,
  investigation planning, knowledge retrieval, autonomous response, guardrails / sandboxing,
  LLM security monitoring, model / prompt defenses).

Notes:
- Methods may involve prompting, tool calling, structured reasoning, RAG, graph / schema retrieval,
  autonomous planning, evaluators, or guardrails.
- Enabling work (datasets, evals, safety, infrastructure) is relevant when explicitly framed for
  LLM / agent security (offense, defense, or securing AI systems).

# Non-Relevance (Exclude)
- Generic AI/ML without a security-ops or AI-security angle.
- Traditional security (rules, signatures, heuristics) without LLMs / agents / RAG.
- Broad privacy, governance, or ethics without concrete LLM / agent security use cases.

# Inputs
- **TITLE:** {title}
- **ABSTRACT:** {abstract}

# Output Fields (handled by caller)
- **relevant:** true / false based on the criteria above.
- **reason:** concise sentence referencing abstract details. Mention the task, red vs. blue (or
  attacking vs. defending AI systems), and how LLMs / agents / RAG are used.

# Decision Rubric
1. Does the work use or analyze LLMs, RAG, or agentic systems? If no → likely false.
2. Is it tied to offensive or defensive security operations (including securing AI systems)?
   If yes → likely true.
3. For enabling work (evals, datasets, safety, infra): is the intended application clearly LLM /
   agent security (offense, defense, or protecting AI systems)? If yes → true, else false.
"""

load_dotenv()

# Reuse or initialize the OpenAI client
llm = OpenAIChatClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_API_MODEL"),
    base_url=os.getenv("OPENAI_API_BASE_URL"),
)


@llm_activity(prompt=LLM_LABEL_PROMPT, llm=llm)
def classify_papers(paper_id: str, title: str, abstract: str) -> PaperClassification:
    """
    Determines if a paper is relevant to LLM/Agentic Security and provides a concise reason.
    """
    ...
