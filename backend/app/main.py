import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.registry import AgentRegistry
from app.api.v1.router import api_v1_router
from app.config import settings
from app.services.database import close_db, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} (env={settings.app_env})")
    await init_db()

    registry = AgentRegistry()
    await registry.discover_and_register()
    app.state.agent_registry = registry

    logger.info("Startup complete")
    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug or settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.debug or settings.app_env != "production" else None,
    lifespan=lifespan,
)

# CORS origins from config (configurable per environment)
cors_origins = [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")
