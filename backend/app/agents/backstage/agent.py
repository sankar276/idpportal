from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.backstage.tools import get_entity_details, list_catalog_entities, search_catalog, trigger_scaffolder_template
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="backstage", description="Manages the Backstage service catalog, entity discovery, and scaffolder templates", capabilities=[
            AgentCapability(name="catalog_management", description="Browse and search the service catalog", tools=["list_catalog_entities", "get_entity_details", "search_catalog"]),
            AgentCapability(name="scaffolding", description="Scaffold new services from templates", tools=["trigger_scaffolder_template"]),
        ])

    def get_tools(self):
        return [list_catalog_entities, get_entity_details, trigger_scaffolder_template, search_catalog]

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
        return "You are a Backstage service catalog agent. You help discover services, browse the catalog, and scaffold new components from templates."
