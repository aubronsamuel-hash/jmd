"""Agent scaffold for AgentObservability."""
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
    """Return the specification for AgentObservability."""
    return AgentSpec(
        name="AgentObservability",
        role="Surveille la sante de la plateforme.",
        responsibilities=["Agreger metrics, traces et logs.", "Evaluer les objectifs SLO.", "Notifier AgentSecurity et AgentPlanner des alertes critiques."],
        inputs=["obs.metric.ingested", "schemas/contracts/agentobservability_contract.json"],
        outputs=["obs.alert.raised", "obs.alert.cleared"],
        guards=["tools/guards/obs_smoke.ps1"],
        topics=["obs.metric.ingested", "obs.alert.raised"],
    )
