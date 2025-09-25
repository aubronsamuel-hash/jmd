"""Agent scaffold for AgentAvailability."""
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
    """Return the specification for AgentAvailability."""
    return AgentSpec(
        name="AgentAvailability",
        role="Collecte les disponibilites et synchronise les contraintes calendrier.",
        responsibilities=["Recevoir les formulaires de disponibilite.", "Generer des instantanes journalises.", "Publier les deltas vers l agent de planification."],
        inputs=["availability.submitted", "schemas/contracts/agentavailability_contract.json"],
        outputs=["availability.snapshot", "agents/AgentAvailability/logs/*.json"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["availability.submitted", "availability.snapshot"],
    )
