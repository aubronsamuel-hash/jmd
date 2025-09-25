"""Agent scaffold for AgentDataOps."""
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
    """Return the specification for AgentDataOps."""
    return AgentSpec(
        name="AgentDataOps",
        role="Orchestre les pipelines data et qualite.",
        responsibilities=["Programmer les pipelines et surveiller les SLA.", "Verifier la qualite des datasets.", "Diffuser les rapports aux autres agents."],
        inputs=["data.pipeline.request", "schemas/contracts/agentdataops_contract.json"],
        outputs=["data.pipeline.completed", "data.quality.issue"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["data.pipeline.completed", "data.quality.issue"],
    )
