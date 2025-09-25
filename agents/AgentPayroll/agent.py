"""Agent scaffold for AgentPayroll."""
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
    """Return the specification for AgentPayroll."""
    return AgentSpec(
        name="AgentPayroll",
        role="Prepare les elements de paie valides.",
        responsibilities=["Recevoir les timesheets approuvees.", "Verifier les grilles tarifaires.", "Publier les lots de paie vers AgentFinance."],
        inputs=["timesheet.approved", "schemas/contracts/agentpayroll_contract.json"],
        outputs=["payroll.ready", "payroll.error"],
        guards=["tools/guards/security_guard.ps1", "tools/guards/qa_guard.ps1"],
        topics=["payroll.ready", "payroll.error"],
    )
