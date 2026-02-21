from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AgentCapability(BaseModel):
    name: str
    description: str
    tools: list[str]


class AgentCard(BaseModel):
    """A2A Agent Card for agent discovery and capability advertisement."""

    name: str
    description: str
    capabilities: list[AgentCapability]
    version: str = "1.0.0"
    protocol: str = "a2a/1.0"


class BaseAgent(ABC):
    """Base class for all platform agents.

    Every agent must implement:
    - get_card(): Return an AgentCard describing capabilities
    - get_tools(): Return MCP-compatible tool definitions
    - invoke(): Execute a task and return a result
    - get_system_prompt(): Return the agent's system prompt
    """

    @abstractmethod
    def get_card(self) -> AgentCard:
        """Return A2A agent card for discovery."""
        ...

    @abstractmethod
    def get_tools(self) -> list[Any]:
        """Return langchain-compatible tool definitions."""
        ...

    @abstractmethod
    async def invoke(self, task: str, context: dict) -> dict:
        """Execute a task and return result.

        Args:
            task: Natural language task description
            context: Contextual information (conversation history, user info, etc.)

        Returns:
            Dict with 'content' (str) and optional 'tools_used' (list[str])
        """
        ...

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent's system prompt."""
        ...
