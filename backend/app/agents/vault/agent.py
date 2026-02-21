from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.vault.tools import create_vault_policy, enable_secrets_engine, list_secrets, read_secret, write_secret
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="vault", description="Manages secrets in HashiCorp Vault (KV-v2 engine)", capabilities=[
            AgentCapability(name="secret_management", description="Read, write, and list secrets", tools=["read_secret", "write_secret", "list_secrets"]),
            AgentCapability(name="policy_management", description="Create Vault policies and manage engines", tools=["create_vault_policy", "enable_secrets_engine"]),
        ])

    def get_tools(self):
        return [read_secret, write_secret, list_secrets, create_vault_policy, enable_secrets_engine]

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
        return "You are a HashiCorp Vault secrets management agent. You manage secrets, policies, and secrets engines. Never expose secret values directly - only confirm operations and show metadata."
