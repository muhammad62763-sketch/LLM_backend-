from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.entities.chat_message import ChatMessage
from app.domain.entities.session import Session


class IChatRepository(ABC):
    """Interface for chat message persistence"""

    @abstractmethod
    async def save_message(self, message: ChatMessage) -> ChatMessage:
        """Save a chat message"""
        pass

    @abstractmethod
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Retrieve chat history for a session"""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete all messages in a session"""
        pass


class ISessionRepository(ABC):
    """Interface for session management"""

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        pass

    @abstractmethod
    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Session]:
        """List all sessions with pagination"""
        pass

    @abstractmethod
    async def create_session(self, session_id: str) -> Session:
        """Create a new session"""
        pass

    @abstractmethod
    async def update_session(self, session_id: str) -> bool:
        """Update session timestamp"""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        pass


class IUsageRepository(ABC):
    """Interface for API usage tracking"""

    @abstractmethod
    async def record_usage(
        self,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Record API usage"""
        pass

    @abstractmethod
    async def get_provider_stats(
        self,
        provider_name: str,
        since: datetime
    ) -> dict:
        """Get usage statistics for a provider"""
        pass

    @abstractmethod
    async def get_total_usage(self, since: datetime) -> dict:
        """Get total usage across all providers"""
        pass
