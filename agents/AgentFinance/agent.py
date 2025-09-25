"""Agent scaffold for AgentFinance."""
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
    """Return the specification for AgentFinance."""
    return AgentSpec(
        name="AgentFinance",
        role="Supervise les ecritures financieres.",
        responsibilities=["Reconciler les lots de paie et la comptabilite.", "Publier les journaux financiers.", "Partager les alertes audits."],
        inputs=["payroll.ready", "schemas/contracts/agentfinance_contract.json"],
        outputs=["finance.entry.created", "finance.audit.flagged"],
        guards=["tools/guards/security_guard.ps1"],
        topics=["finance.entry.created", "finance.audit.flagged"],
    )
