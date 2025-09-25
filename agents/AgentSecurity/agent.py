"""Agent scaffold for AgentSecurity."""
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
    """Return the specification for AgentSecurity."""
    return AgentSpec(
        name="AgentSecurity",
        role="Assure la posture de securite globale.",
        responsibilities=["Analyser les evenements de securite.", "Orchestrer les reponses et escalades.", "Partager les avis de conformite."],
        inputs=["security.events", "schemas/contracts/agentsecurity_contract.json"],
        outputs=["security.alert", "security.clearance"],
        guards=["tools/guards/security_guard.ps1"],
        topics=["security.alert", "security.clearance"],
    )
