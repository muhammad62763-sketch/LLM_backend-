from typing import Optional
from uuid import uuid4
from app.domain.entities.chat_message import ChatMessage, MessageRole
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.infrastructure.services.multi_api_service import MultiAPIService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatUseCase:
    """Use case for chat operations following Clean Architecture"""
    
    def __init__(
        self,
        multi_api_service: MultiAPIService
    ):
        self.multi_api_service = multi_api_service
    
    async def send_message(
        self,
        uow: IUnitOfWork,
        message_content: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> dict:
        """
        Send a chat message and get AI response
        
        Args:
            uow: Unit of Work
            message_content: User message
            session_id: Chat session ID (creates new if None)
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
        
        Returns:
            Dict with response and metadata
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())
            logger.info("New session created", session_id=session_id)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            content=message_content
        )
        await uow.chat_repo.save_message(user_message)
        
        # Get AI response
        response = await self.multi_api_service.chat_completion(
            message=message_content,
            uow=uow,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response["content"],
            provider_used=response["provider"],
            model_used=response["model"],
            tokens_used=response["tokens_used"]
        )
        await uow.chat_repo.save_message(assistant_message)
        
        await uow.commit()
        
        logger.info(
            "Chat exchange completed",
            session_id=session_id,
            provider=response["provider"],
            tokens=response["tokens_used"]
        )
        
        return {
            "session_id": session_id,
            "response": response["content"],
            "provider_used": response["provider"],
            "model": response["model"],
            "tokens_used": response["tokens_used"],
            "response_time": response["response_time"]
        }
    
    async def get_chat_history(
        self,
        uow: IUnitOfWork,
        session_id: str,
        limit: int = 50
    ) -> list:
        """Get chat history for a session"""
        logger.info("Fetching chat history", session_id=session_id)
        
        messages = await uow.chat_repo.get_session_history(session_id, limit)
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "provider_used": msg.provider_used,
                "model_used": msg.model_used,
                "tokens_used": msg.tokens_used,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    
    async def delete_session(
        self,
        uow: IUnitOfWork,
        session_id: str
    ) -> bool:
        """Delete a chat session"""
        logger.info("Deleting session", session_id=session_id)
        
        deleted = await uow.chat_repo.delete_session(session_id)
        await uow.commit()
        
        return deleted
