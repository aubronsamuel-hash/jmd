"""Agent scaffold for AgentUISystem."""
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
    """Return the specification for AgentUISystem."""
    return AgentSpec(
        name="AgentUISystem",
        role="Gere le design system et la coherence UI.",
        responsibilities=["Publier les composants UI.", "Auditer l accessibilite.", "Notifier AgentDocs des changements UX."],
        inputs=["ui.component.request", "schemas/contracts/agentuisystem_contract.json"],
        outputs=["ui.component.released", "ui.audit.failed"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["ui.component.released", "ui.audit.failed"],
    )
