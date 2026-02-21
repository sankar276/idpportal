import json
import logging
from typing import Any, AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from app.agents.registry import AgentRegistry
from app.config import Settings
from app.services.llm import get_llm

logger = logging.getLogger(__name__)


class OrchestratorState(BaseModel):
    messages: list[Any] = []
    conversation_id: str = ""
    current_task: str = ""
    next_agent: str = ""
    agent_outputs: dict = {}
    context: dict = {}


class SupervisorAgent:
    def __init__(self, registry: AgentRegistry, settings: Settings):
        self.registry = registry
        self.settings = settings
        self.llm = get_llm(settings)

    def _build_supervisor_prompt(self) -> str:
        agent_descriptions = self.registry.get_agent_descriptions()
        return f"""You are the IDP Portal Supervisor Agent. You orchestrate platform engineering tasks
by delegating to specialized sub-agents.

Available agents:
{agent_descriptions}

When a user sends a message:
1. Analyze what they need
2. Decide which agent(s) to delegate to
3. If the task requires multiple agents, execute them in the right order
4. Synthesize the results into a clear response

Respond with a JSON object:
{{
    "reasoning": "your analysis of what needs to be done",
    "agent": "agent_name" or null if you can answer directly,
    "task": "specific task to delegate" or null,
    "response": "direct response if no agent needed" or null
}}

If the task is complete, set "agent" to null and provide the final "response"."""

    async def run(self, user_message: str, conversation_id: str = "") -> dict:
        state = OrchestratorState(
            messages=[HumanMessage(content=user_message)],
            conversation_id=conversation_id,
        )

        supervisor_prompt = self._build_supervisor_prompt()
        max_iterations = 5

        for _iteration in range(max_iterations):
            messages = [
                SystemMessage(content=supervisor_prompt),
                *state.messages,
            ]

            response = await self.llm.ainvoke(messages)
            response_text = response.content

            try:
                decision = json.loads(response_text)
            except json.JSONDecodeError:
                # LLM gave a direct text response
                state.messages.append(AIMessage(content=response_text))
                break

            agent_name = decision.get("agent")
            task = decision.get("task")
            direct_response = decision.get("response")

            if not agent_name:
                final_msg = direct_response or "Task completed."
                state.messages.append(AIMessage(content=final_msg))
                break

            agent = self.registry.get_agent(agent_name)
            if not agent:
                state.messages.append(
                    AIMessage(content=f"Agent '{agent_name}' not available. {direct_response or ''}")
                )
                break

            try:
                result = await agent.invoke(task=task, context=state.context)
                state.agent_outputs[agent_name] = result
                state.messages.append(
                    AIMessage(
                        content=f"[{agent_name} agent]: {result.get('content', 'Done')}",
                        name=agent_name,
                    )
                )
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                state.messages.append(
                    AIMessage(content=f"[{agent_name} agent] Error: {str(e)}")
                )

        return {
            "messages": state.messages,
            "agent_outputs": state.agent_outputs,
            "conversation_id": conversation_id,
        }

    async def stream(
        self, user_message: str, conversation_id: str = ""
    ) -> AsyncIterator[dict]:
        """Stream events for real-time UI updates."""
        yield {"type": "thinking", "content": "Analyzing your request..."}

        result = await self.run(user_message, conversation_id)

        for name, output in result.get("agent_outputs", {}).items():
            yield {
                "type": "agent_output",
                "agent": name,
                "content": output.get("content", ""),
                "tools_used": output.get("tools_used", []),
            }

        if result.get("messages"):
            last_msg = result["messages"][-1]
            yield {
                "type": "message",
                "content": last_msg.content if hasattr(last_msg, "content") else str(last_msg),
                "conversation_id": conversation_id,
            }

        yield {"type": "done"}
