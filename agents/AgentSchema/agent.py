"""Agent scaffold for AgentSchema."""
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
    """Return the specification for AgentSchema."""
    return AgentSpec(
        name="AgentSchema",
        role="Definit les contrats JSON et gere le versionning des schemas.",
        responsibilities=[
            "Maintenir schemas/contracts/*.json",
            "Publier les migrations necessaires",
            "Valider la compatibilite avec les agents consommateurs",
        ],
        inputs=[
            "schemas/contracts/*.json",
            "docs/agents/AGENT.AgentSchema.md",
        ],
        outputs=[
            "schemas/contracts/version-manifest.json",
            "Rapports schema_guard",
        ],
        guards=[
            "tools/guards/schema_guard.ps1",
        ],
        topics=[
            "schema.contract.published",
            "schema.contract.deprecated",
        ],
    )
