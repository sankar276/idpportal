from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.github.tools import (
    create_issue,
    create_pull_request,
    create_repository,
    get_workflow_runs,
    list_repositories,
    search_code,
)
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(
            name="github",
            description="Manages GitHub repositories, pull requests, issues, and CI/CD workflows",
            capabilities=[
                AgentCapability(
                    name="repository_management",
                    description="Create, list, and search repositories",
                    tools=["create_repository", "list_repositories", "search_code"],
                ),
                AgentCapability(
                    name="pull_request_management",
                    description="Create and manage pull requests",
                    tools=["create_pull_request"],
                ),
                AgentCapability(
                    name="issue_tracking",
                    description="Create and manage issues",
                    tools=["create_issue"],
                ),
                AgentCapability(
                    name="ci_cd",
                    description="Monitor GitHub Actions workflows",
                    tools=["get_workflow_runs"],
                ),
            ],
        )

    def get_tools(self):
        return [
            create_repository,
            create_pull_request,
            list_repositories,
            create_issue,
            search_code,
            get_workflow_runs,
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

                    messages.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                    )

            final_response = await llm_with_tools.ainvoke(messages)
            return {"content": final_response.content, "tools_used": tools_used}

        return {"content": response.content, "tools_used": []}

    def get_system_prompt(self) -> str:
        return """You are a GitHub operations agent for the IDP Portal.
You help platform engineers and developers manage GitHub repositories, pull requests,
issues, and CI/CD workflows. Use the available tools to fulfill requests.
Always confirm destructive actions before executing them."""
