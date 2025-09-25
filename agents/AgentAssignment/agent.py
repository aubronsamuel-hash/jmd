"""Agent scaffold for AgentAssignment."""
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
    """Return the specification for AgentAssignment."""
    return AgentSpec(
        name="AgentAssignment",
        role="Assigne les talents aux missions.",
        responsibilities=["Recevoir les propositions de planning.", "Valider la conformite contractuelle.", "Publier les affectations definitives."],
        inputs=["schedule.generated", "schemas/contracts/agentassignment_contract.json"],
        outputs=["assignment.created", "assignment.updated"],
        guards=["tools/guards/qa_guard.ps1", "tools/guards/security_guard.ps1"],
        topics=["assignment.created", "assignment.updated"],
    )
