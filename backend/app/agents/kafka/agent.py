from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.kafka.tools import create_topic, delete_topic, describe_topic, list_topics, update_topic_config
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="kafka", description="Manages Kafka topics via Strimzi KafkaTopic CRDs", capabilities=[
            AgentCapability(name="topic_management", description="Create, list, describe, update, and delete Kafka topics", tools=["create_topic", "list_topics", "describe_topic", "update_topic_config", "delete_topic"]),
        ])

    def get_tools(self):
        return [create_topic, list_topics, describe_topic, update_topic_config, delete_topic]

    async def invoke(self, task: str, context: dict) -> dict:
        llm = get_llm(settings)
        tools = self.get_tools()
        llm_with_tools = llm.bind_tools(tools)
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
        messages = [SystemMessage(content=self.get_system_prompt()), HumanMessage(content=task)]
        response = await llm_with_tools.ainvoke(messages)
        tools_used = []
        if response.tool_calls:
            tool_map = {t.name: t for t in tools}
            for tc in response.tool_calls:
                fn = tool_map.get(tc["name"])
                if fn:
                    result = await fn.ainvoke(tc["args"])
                    tools_used.append(tc["name"])
                    messages.append(response)
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            final = await llm_with_tools.ainvoke(messages)
            return {"content": final.content, "tools_used": tools_used}
        return {"content": response.content, "tools_used": []}

    def get_system_prompt(self) -> str:
        return "You are a Kafka operations agent. You manage Kafka topics via Strimzi KafkaTopic CRDs on Kubernetes. You can create, list, describe, update config, and delete topics."
