import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

logger = logging.getLogger(__name__)

engine = None
async_session_factory = None


def _create_engine():
    global engine, async_session_factory
    if not settings.database_url:
        logger.warning("DATABASE_URL not set - database features disabled")
        return
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
    )
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database engine and verify connectivity."""
    _create_engine()
    if engine is None:
        logger.warning("Skipping database initialization - no DATABASE_URL")
        return
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text

            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        if settings.app_env == "production":
            raise
        logger.warning("Continuing without database in non-production mode")


async def close_db():
    """Close the database engine and release connections."""
    global engine
    if engine is not None:
        await engine.dispose()
        logger.info("Database connections closed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Set DATABASE_URL environment variable.")
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {type(e).__name__}: {e}")
            raise
