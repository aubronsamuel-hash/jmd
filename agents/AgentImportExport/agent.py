"""Agent scaffold for AgentImportExport."""
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
    """Return the specification for AgentImportExport."""
    return AgentSpec(
        name="AgentImportExport",
        role="Automatise les flux d import/export de donnees.",
        responsibilities=["Planifier les jobs d echange.", "Verifier les checksums entrants.", "Notifier AgentDataOps des resultats."],
        inputs=["import.requested", "schemas/contracts/agentimportexport_contract.json"],
        outputs=["import.completed", "export.completed"],
        guards=["tools/guards/security_guard.ps1"],
        topics=["import.completed", "export.completed"],
    )
