from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.argocd.tools import (
    get_application_status,
    get_deployment_history,
    list_applications,
    rollback_application,
    sync_application,
)
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(
            name="argocd",
            description="Manages ArgoCD applications, deployments, syncs, and rollbacks",
            capabilities=[
                AgentCapability(
                    name="deployment_management",
                    description="List, sync, and rollback applications",
                    tools=["list_applications", "sync_application", "rollback_application"],
                ),
                AgentCapability(
                    name="deployment_monitoring",
                    description="Check application status and deployment history",
                    tools=["get_application_status", "get_deployment_history"],
                ),
            ],
        )

    def get_tools(self):
        return [
            list_applications,
            get_application_status,
            sync_application,
            rollback_application,
            get_deployment_history,
        ]

    async def invoke(self, task: str, context: dict) -> dict:
        llm = get_llm(settings)
        tools = self.get_tools()
        llm_with_tools = llm.bind_tools(tools)

        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=task),
        ]

        response = await llm_with_tools.ainvoke(messages)
        tools_used = []

        if response.tool_calls:
            tool_map = {t.name: t for t in tools}
            for tool_call in response.tool_calls:
                tool_fn = tool_map.get(tool_call["name"])
                if tool_fn:
                    result = await tool_fn.ainvoke(tool_call["args"])
                    tools_used.append(tool_call["name"])
                    messages.append(response)
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

            final_response = await llm_with_tools.ainvoke(messages)
            return {"content": final_response.content, "tools_used": tools_used}

        return {"content": response.content, "tools_used": []}

    def get_system_prompt(self) -> str:
        return """You are an ArgoCD operations agent for the IDP Portal.
You manage application deployments through ArgoCD GitOps.
You can list applications, check their sync/health status, trigger syncs, and perform rollbacks.
Always check application status before performing sync or rollback operations."""
