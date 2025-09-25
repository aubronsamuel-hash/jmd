"""Agent scaffold for AgentTimesheet."""
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
    """Return the specification for AgentTimesheet."""
    return AgentSpec(
        name="AgentTimesheet",
        role="Controle et valide les heures travaillees.",
        responsibilities=["Collecter les timesheets par mission.", "Verrouiller les timesheets apres validation.", "Notifier AgentPayroll des statuts."],
        inputs=["timesheet.submitted", "schemas/contracts/agenttimesheet_contract.json"],
        outputs=["timesheet.approved", "timesheet.rejected"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["timesheet.submitted", "timesheet.approved"],
    )
