"""Agent scaffold for AgentQA."""
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
    """Return the specification for AgentQA."""
    return AgentSpec(
        name="AgentQA",
        role="Coordonne les tests automatises et manuels.",
        responsibilities=["Planifier les suites de tests.", "Collecter les rapports de couverture.", "Publier les verdicts vers AgentPlanner."],
        inputs=["qa.test.plan", "schemas/contracts/agentqa_contract.json"],
        outputs=["qa.test.run", "qa.test.failed"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["qa.test.run", "qa.test.failed"],
    )
