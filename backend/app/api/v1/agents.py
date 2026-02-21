from fastapi import APIRouter, Request

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/")
async def list_agents(request: Request):
    registry = request.app.state.agent_registry
    agents = []
    for name in registry.list_agents():
        agent = registry.get_agent(name)
        card = agent.get_card()
        agents.append(card.model_dump())
    return {"agents": agents}


@router.get("/{agent_name}")
async def get_agent(agent_name: str, request: Request):
    registry = request.app.state.agent_registry
    agent = registry.get_agent(agent_name)
    if not agent:
        return {"error": f"Agent '{agent_name}' not found"}, 404
    return agent.get_card().model_dump()


@router.get("/{agent_name}/tools")
async def get_agent_tools(agent_name: str, request: Request):
    registry = request.app.state.agent_registry
    agent = registry.get_agent(agent_name)
    if not agent:
        return {"error": f"Agent '{agent_name}' not found"}, 404
    tools = agent.get_tools()
    return {
        "agent": agent_name,
        "tools": [{"name": t.name, "description": t.description} for t in tools],
    }
