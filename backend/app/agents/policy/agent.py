from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.policy.tools import fix_violations, generate_config, list_policies, validate_config
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="policy", description="Validates configs against OPA/Rego policies, generates compliant configs, and auto-fixes violations using AI", capabilities=[
            AgentCapability(name="validation", description="Validate configurations against policies", tools=["validate_config", "list_policies"]),
            AgentCapability(name="generation", description="Generate policy-compliant configs from requirements", tools=["generate_config"]),
            AgentCapability(name="remediation", description="Auto-fix policy violations", tools=["fix_violations"]),
        ])

    def get_tools(self):
        return [validate_config, generate_config, fix_violations, list_policies]

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
        return """You are a Policy validation agent powered by OPA/Rego. You validate infrastructure and application
configurations against organizational policies across domains: kafka, kubernetes, terraform, cicd, gitops.
You can generate compliant configurations from natural language and auto-fix policy violations using AI."""
