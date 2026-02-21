from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.agents.supervisor import SupervisorAgent
from app.config import settings
from app.services.auth import verify_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    if settings.app_env == "development" and not credentials:
        return {"sub": "dev-user", "email": "dev@localhost", "roles": ["admin"]}
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await verify_token(credentials.credentials)


async def get_supervisor(request: Request) -> SupervisorAgent:
    registry = request.app.state.agent_registry
    return SupervisorAgent(registry=registry, settings=settings)
