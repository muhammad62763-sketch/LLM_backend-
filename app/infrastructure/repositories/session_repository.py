from typing import List, Optional
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories import ISessionRepository
from app.domain.entities.session import Session
from app.infrastructure.database.models import ChatSessionModel, ChatMessageModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class SessionRepository(ISessionRepository):
    """Implementation of session repository using SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID with aggregated data"""
        logger.info("Fetching session", session_id=session_id)

        # Get session with message count and last message timestamp
        stmt = select(
            ChatSessionModel.session_id,
            ChatSessionModel.created_at,
            ChatSessionModel.updated_at,
            func.count(ChatMessageModel.id).label('message_count'),
            func.max(ChatMessageModel.created_at).label('last_message_at')
        ).select_from(
            ChatSessionModel
        ).outerjoin(
            ChatMessageModel,
            ChatSessionModel.session_id == ChatMessageModel.session_id
        ).where(
            ChatSessionModel.session_id == session_id
        ).group_by(
            ChatSessionModel.session_id,
            ChatSessionModel.created_at,
            ChatSessionModel.updated_at
        )

        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            return None

        return Session(
            session_id=row.session_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
            message_count=row.message_count or 0,
            last_message_at=row.last_message_at
        )

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Session]:
        """List all sessions with pagination and aggregated data"""
        logger.info("Listing sessions", limit=limit, offset=offset)

        # Get sessions with message counts and last activity
        stmt = select(
            ChatSessionModel.session_id,
            ChatSessionModel.created_at,
            ChatSessionModel.updated_at,
            func.count(ChatMessageModel.id).label('message_count'),
            func.max(ChatMessageModel.created_at).label('last_message_at')
        ).select_from(
            ChatSessionModel
        ).outerjoin(
            ChatMessageModel,
            ChatSessionModel.session_id == ChatMessageModel.session_id
        ).group_by(
            ChatSessionModel.session_id,
            ChatSessionModel.created_at,
            ChatSessionModel.updated_at
        ).order_by(
            ChatSessionModel.updated_at.desc()
        ).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            Session(
                session_id=row.session_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
                message_count=row.message_count or 0,
                last_message_at=row.last_message_at
            )
            for row in rows
        ]

    async def create_session(self, session_id: str) -> Session:
        """Create a new session"""
        logger.info("Creating session", session_id=session_id)

        session_model = ChatSessionModel(session_id=session_id)
        self.session.add(session_model)
        await self.session.flush()

        return Session(
            session_id=session_id,
            created_at=session_model.created_at,
            updated_at=session_model.updated_at
        )

    async def update_session(self, session_id: str) -> bool:
        """Update session timestamp"""
        logger.info("Updating session timestamp", session_id=session_id)

        stmt = update(ChatSessionModel).where(
            ChatSessionModel.session_id == session_id
        ).values(updated_at=func.now())

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        logger.info("Deleting session", session_id=session_id)

        stmt = delete(ChatSessionModel).where(
            ChatSessionModel.session_id == session_id
        )
        result = await self.session.execute(stmt)

        return result.rowcount > 0
