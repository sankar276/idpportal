import json
import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.agents.supervisor import SupervisorAgent
from app.api.deps import get_supervisor

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AgentOutput(BaseModel):
    agent_name: str
    content: str
    tools_used: list[str] = []


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    agent_outputs: list[AgentOutput] = []


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, supervisor: SupervisorAgent = Depends(get_supervisor)):
    result = await supervisor.run(
        user_message=request.message,
        conversation_id=request.conversation_id,
    )

    agent_outputs = []
    for name, output in result.get("agent_outputs", {}).items():
        agent_outputs.append(
            AgentOutput(
                agent_name=name,
                content=str(output.get("content", "")),
                tools_used=output.get("tools_used", []),
            )
        )

    return ChatResponse(
        message=result["messages"][-1].content if result.get("messages") else "",
        conversation_id=request.conversation_id,
        agent_outputs=agent_outputs,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    req: Request,
    supervisor: SupervisorAgent = Depends(get_supervisor),
):
    async def event_generator():
        try:
            async for event in supervisor.stream(
                user_message=request.message,
                conversation_id=request.conversation_id,
            ):
                if await req.is_disconnected():
                    break
                yield {
                    "event": event.get("type", "message"),
                    "data": json.dumps(event),
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())
