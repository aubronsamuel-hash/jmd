"""Agent scaffold for AgentIntegrations."""
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
    """Return the specification for AgentIntegrations."""
    return AgentSpec(
        name="AgentIntegrations",
        role="Gere les connecteurs externes.",
        responsibilities=["Superviser l etat des APIs partenaires.", "Gerer les reauthentifications.", "Publier les alertes de degradation."],
        inputs=["integration.status", "schemas/contracts/agentintegrations_contract.json"],
        outputs=["integration.connected", "integration.failed"],
        guards=["tools/guards/security_guard.ps1"],
        topics=["integration.connected", "integration.failed"],
    )
