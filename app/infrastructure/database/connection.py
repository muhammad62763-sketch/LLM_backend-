from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class DatabaseManager:
    """Manages database connections with Neon PostgreSQL"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
    
    def create_engine(self) -> AsyncEngine:
        """Create async engine with Neon-optimized settings"""
        logger.info("Creating database engine", database_url=self.database_url[:30] + "...")
        
        self._engine = create_async_engine(
            self.database_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,  # Check connection validity
            pool_size=10,
            max_overflow=20,
            pool_recycle=300,  # Recycle connections every 5 min (Neon auto-suspend)
            connect_args={
                "server_settings": {
                    "application_name": settings.APP_NAME,
                    "jit": "off"  # Optimize for serverless
                }
            }
        )
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        return self._engine
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        if not self._session_factory:
            raise RuntimeError("Engine not initialized. Call create_engine() first")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Close all database connections"""
        if self._engine:
            logger.info("Closing database connections")
            await self._engine.dispose()


# Global database manager instance
db_manager = DatabaseManager(settings.DATABASE_URL)
