"""Chat repository implementation"""

from typing import List, Optional
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories import IChatRepository
from app.domain.entities.chat_message import ChatMessage, MessageRole
from app.infrastructure.database.models import ChatMessageModel, ChatSessionModel
from app.core.logging import get_logger


logger = get_logger(__name__)


class ChatRepository(IChatRepository):
    """Implementation of chat repository using SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_message(self, message: ChatMessage) -> ChatMessage:
        """Save a chat message to database"""
        logger.info("Saving message", session_id=message.session_id, role=message.role)
        
        # Ensure session exists
        stmt = select(ChatSessionModel).where(
            ChatSessionModel.session_id == message.session_id
        )
        result = await self.session.execute(stmt)
        session_model = result.scalar_one_or_none()
        
        if not session_model:
            session_model = ChatSessionModel(session_id=message.session_id)
            self.session.add(session_model)
            await self.session.flush()
        
        # Save message
        message_model = ChatMessageModel(
            session_id=message.session_id,
            role=message.role.value,
            content=message.content,
            provider_used=message.provider_used,
            model_used=message.model_used,
            tokens_used=message.tokens_used
        )
        
        self.session.add(message_model)
        await self.session.flush()
        
        return message
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Retrieve chat history for a session"""
        logger.info("Fetching session history", session_id=session_id, limit=limit)
        
        stmt = select(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        ).order_by(
            ChatMessageModel.created_at
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [
            ChatMessage(
                session_id=m.session_id,
                role=MessageRole(m.role),
                content=m.content,
                provider_used=m.provider_used,
                model_used=m.model_used,
                tokens_used=m.tokens_used,
                created_at=m.created_at
            )
            for m in models
        ]
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessageModel]:
        """Get all messages for a session (returns raw models)"""
        logger.info("Fetching session messages", session_id=session_id, limit=limit)
        
        stmt = select(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        ).order_by(
            ChatMessageModel.created_at.asc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        return list(messages)
    
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatMessageModel]:
        """Get recent messages for a session"""
        logger.info("Fetching recent messages", session_id=session_id, limit=limit)
        
        stmt = select(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        ).order_by(
            desc(ChatMessageModel.created_at)
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        return list(reversed(messages))
    
    async def create_message(
        self,
        session_id: str,
        role: str,
        content: str,
        provider_used: Optional[str] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> ChatMessageModel:
        """Create a new chat message"""
        logger.info("Creating message", session_id=session_id, role=role)
        
        message = ChatMessageModel(
            session_id=session_id,
            role=role,
            content=content,
            provider_used=provider_used,
            model_used=model_used,
            tokens_used=tokens_used
        )
        
        self.session.add(message)
        await self.session.flush()
        
        return message
    
    async def get_message_by_id(self, message_id: int) -> Optional[ChatMessageModel]:
        """Get a specific message by ID"""
        stmt = select(ChatMessageModel).where(ChatMessageModel.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete all messages and session"""
        logger.info("Deleting session", session_id=session_id)
        
        # Delete messages first
        stmt = delete(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        )
        await self.session.execute(stmt)
        
        # Delete session
        stmt = delete(ChatSessionModel).where(
            ChatSessionModel.session_id == session_id
        )
        result = await self.session.execute(stmt)
        
        return result.rowcount > 0
    
    async def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages for a session (keep session)"""
        logger.info("Deleting session messages", session_id=session_id)
        
        stmt = delete(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        )
        result = await self.session.execute(stmt)
        
        return result.rowcount
    
    async def get_or_create_session(self, session_id: str) -> ChatSessionModel:
        """Get existing session or create new one"""
        stmt = select(ChatSessionModel).where(
            ChatSessionModel.session_id == session_id
        )
        result = await self.session.execute(stmt)
        session_model = result.scalar_one_or_none()
        
        if not session_model:
            logger.info("Creating new session", session_id=session_id)
            session_model = ChatSessionModel(session_id=session_id)
            self.session.add(session_model)
            await self.session.flush()
        
        return session_model
    
    async def get_all_sessions(self, limit: int = 100) -> List[ChatSessionModel]:
        """Get all chat sessions"""
        stmt = select(ChatSessionModel).order_by(
            desc(ChatSessionModel.created_at)
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        stmt = select(ChatSessionModel).where(
            ChatSessionModel.session_id == session_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_session_count(self, session_id: str) -> int:
        """Get message count for a session"""
        stmt = select(ChatMessageModel).where(
            ChatMessageModel.session_id == session_id
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        return len(messages)
