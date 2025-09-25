"""Agent scaffold for AgentNotifications."""
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
    """Return the specification for AgentNotifications."""
    return AgentSpec(
        name="AgentNotifications",
        role="Diffuse les notifications multicanal.",
        responsibilities=["Orchestrer les canaux email, sms et push.", "Gerer les echecs de livraison.", "Reporter la trace d envoi aux autres agents."],
        inputs=["notification.queue", "schemas/contracts/agentnotifications_contract.json"],
        outputs=["notification.dispatch", "notification.error"],
        guards=["tools/guards/qa_guard.ps1"],
        topics=["notification.dispatch", "notification.error"],
    )
