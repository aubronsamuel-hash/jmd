"""Agent scaffold for AgentPlanner."""
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
    """Return the specification for AgentPlanner."""
    return AgentSpec(
        name="AgentPlanner",
        role="Pilote la decomposition roadmap et la creation des steps.",
        responsibilities=[
            "Analyser les besoins issus de docs/roadmap.",
            "Decouper les objectifs en sous-etapes et fixer les references.",
            "Coordonner la creation des tickets agents et synchroniser les docs roadmap.",
        ],
        inputs=[
            "docs/roadmap/ROADMAP.template-step.md",
            "schemas/contracts/agentplanner_contract.json",
        ],
        outputs=[
            "docs/roadmap/step-XX.md",
            "docs/roadmap/step-XX.1.md pour mode FIX",
            ".codex/latest/last_output.json",
        ],
        guards=[
            "tools/guards/roadmap_guard.ps1",
            "tools/guards/archive_guard.ps1",
        ],
        topics=[
            "roadmap.plan",
            "roadmap.progress",
        ],
    )
