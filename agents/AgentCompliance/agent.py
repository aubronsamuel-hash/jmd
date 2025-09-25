"""Agent scaffold for AgentCompliance."""
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
    """Return the specification for AgentCompliance."""
    return AgentSpec(
        name="AgentCompliance",
        role="Pilote les controles juridiques et sociaux.",
        responsibilities=["Verifier les obligations legales.", "Publier des rapports de conformite.", "Alerter AgentSecurity en cas d incident."],
        inputs=["compliance.ruleset", "schemas/contracts/agentcompliance_contract.json"],
        outputs=["compliance.check.passed", "compliance.check.failed"],
        guards=["tools/guards/security_guard.ps1"],
        topics=["compliance.check.passed", "compliance.check.failed"],
    )
