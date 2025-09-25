"""Agent scaffold for AgentDocs."""
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
    """Return the specification for AgentDocs."""
    return AgentSpec(
        name="AgentDocs",
        role="Maintient l alignement documentaire.",
        responsibilities=["Mettre a jour les AGENT.*.md.", "Garantir la coherence du changelog.", "Publier les journaux last_output.json."],
        inputs=["docs.updated", "schemas/contracts/agentdocs_contract.json"],
        outputs=["docs.review.required", "docs.updated"],
        guards=["tools/guards/docs_guard.ps1", "tools/guards/archive_guard.ps1"],
        topics=["docs.updated", "docs.review.required"],
    )
