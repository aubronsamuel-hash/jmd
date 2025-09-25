"""Agent scaffold for AgentLLMEvaluator."""
from dataclasses import dataclass
from typing import List


@dataclass
class AgentSpec:
    name: str
    role: str
    responsibilities: List[str]
    inputs: List[str]
    outputs: List[str]
    guards: List[str]
    topics: List[str]


def get_agent_spec() -> AgentSpec:
    """Return the specification for AgentLLMEvaluator."""
    return AgentSpec(
        name="AgentLLMEvaluator",
        role="Evalue et note les generations LLM.",
        responsibilities=["Collecter les sorties IA.", "Comparer aux criteres de qualite.", "Publier les resultats pour AgentQA et AgentDocs."],
        inputs=["llm.eval.request", "schemas/contracts/agentllmevaluator_contract.json"],
        outputs=["llm.eval.completed", "llm.eval.flagged"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["llm.eval.completed", "llm.eval.flagged"],
    )
