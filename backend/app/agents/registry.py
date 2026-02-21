import importlib
import logging

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)

AGENT_MODULES = [
    "app.agents.github.agent",
    "app.agents.argocd.agent",
    "app.agents.flux.agent",
    "app.agents.jira.agent",
    "app.agents.slack.agent",
    "app.agents.pagerduty.agent",
    "app.agents.backstage.agent",
    "app.agents.kafka.agent",
    "app.agents.vault.agent",
    "app.agents.rancher.agent",
    "app.agents.policy.agent",
]


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    async def discover_and_register(self):
        for module_path in AGENT_MODULES:
            try:
                module = importlib.import_module(module_path)
                agent_class = getattr(module, "Agent")
                agent = agent_class()
                card = agent.get_card()
                self._agents[card.name] = agent
                logger.info(f"Registered agent: {card.name}")
            except Exception as e:
                logger.warning(f"Failed to load agent from {module_path}: {e}")

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    def get_all_tools(self) -> list:
        tools = []
        for agent in self._agents.values():
            tools.extend(agent.get_tools())
        return tools

    def get_agent_descriptions(self) -> str:
        """Return a formatted string of all agent capabilities for the supervisor."""
        descriptions = []
        for name, agent in self._agents.items():
            card = agent.get_card()
            caps = ", ".join(c.name for c in card.capabilities)
            descriptions.append(f"- **{name}**: {card.description} (capabilities: {caps})")
        return "\n".join(descriptions)
