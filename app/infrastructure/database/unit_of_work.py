from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.usage_repository import UsageRepository
from app.infrastructure.repositories.session_repository import SessionRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class UnitOfWork(IUnitOfWork):
    """Unit of Work implementation with SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self._session = session
        self.chat_repo = ChatRepository(session)
        self.usage_repo = UsageRepository(session)
        self.session_repo = SessionRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        """Enter async context"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and handle commit/rollback"""
        if exc_type is not None:
            await self.rollback()
            logger.error("Transaction rolled back", exception=str(exc_val))
        else:
            await self.commit()

    async def commit(self) -> None:
        """Commit transaction"""
        await self._session.commit()
        logger.debug("Transaction committed")

    async def rollback(self) -> None:
        """Rollback transaction"""
        await self._session.rollback()
        logger.debug("Transaction rolled back")
