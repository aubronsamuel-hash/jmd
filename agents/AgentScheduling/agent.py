"""Agent scaffold for AgentScheduling."""
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
    """Return the specification for AgentScheduling."""
    return AgentSpec(
        name="AgentScheduling",
        role="Optimise le planning global.",
        responsibilities=["Agreger les disponibilites et contraintes.", "Proposer des plannings resolvant les conflits.", "Publier les versions valides aux agents aval."],
        inputs=["availability.snapshot", "schemas/contracts/agentscheduling_contract.json"],
        outputs=["schedule.generated", "schedule.conflict"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["schedule.generated", "schedule.conflict"],
    )
