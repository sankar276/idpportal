from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.jira.tools import add_comment, create_jira_issue, get_sprint_board, search_issues, update_issue_status
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="jira", description="Manages Jira issues, sprints, and project tracking", capabilities=[
            AgentCapability(name="issue_management", description="Create, search, and update Jira issues", tools=["create_jira_issue", "search_issues", "update_issue_status", "add_comment"]),
            AgentCapability(name="sprint_tracking", description="View sprint boards and progress", tools=["get_sprint_board"]),
        ])

    def get_tools(self):
        return [create_jira_issue, search_issues, update_issue_status, get_sprint_board, add_comment]

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
        return "You are a Jira project management agent. You help manage issues, track sprints, and coordinate work across teams."
