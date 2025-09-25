"""Agent scaffold for AgentInventory."""
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
    """Return the specification for AgentInventory."""
    return AgentSpec(
        name="AgentInventory",
        role="Suit les ressources materiel et logistique.",
        responsibilities=["Enregistrer les demandes de materiel.", "Reserver et liberer les ressources.", "Assurer la tracabilite pour AgentCompliance."],
        inputs=["inventory.requested", "schemas/contracts/agentinventory_contract.json"],
        outputs=["inventory.reserved", "inventory.released"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["inventory.reserved", "inventory.released"],
    )
