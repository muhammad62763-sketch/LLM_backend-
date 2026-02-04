from abc import ABC, abstractmethod
from typing import Protocol
from app.domain.interfaces.repositories import IChatRepository, IUsageRepository, ISessionRepository


class IUnitOfWork(ABC):
    """Unit of Work pattern for transaction management"""

    chat_repo: IChatRepository
    usage_repo: IUsageRepository
    session_repo: ISessionRepository
    
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enter async context"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and handle commit/rollback"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction"""
        pass
