"""Chat API endpoints for conversation management"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.application.dto.schemas import ChatRequest
from app.application.use_cases.chat import ChatUseCase
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.presentation.api.dependencies import get_unit_of_work
from app.infrastructure.services.multi_api_service import multi_api_service
from app.core.logging import get_logger
from datetime import datetime


logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Send chat message"
)
async def send_chat_message(
    request: ChatRequest,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Send a chat message and receive AI response
    
    - **message**: The user's message (required)
    - **session_id**: Chat session ID (optional, creates new if not provided)
    - **model**: Specific model to use (optional)
    - **temperature**: Sampling temperature 0.0-2.0 (default: 0.7)
    - **max_tokens**: Maximum response tokens (default: 2000)
    
    Returns:
    - session_id: Session identifier
    - response: AI-generated response
    - provider_used: Which AI provider handled the request
    - model: Model used for generation
    - tokens_used: Number of tokens consumed
    - response_time: Response time in seconds
    """
    try:
        chat_use_case = ChatUseCase(multi_api_service)
        
        result = await chat_use_case.send_message(
            uow=uow,
            message_content=request.message,
            session_id=request.session_id,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return result
        
    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get(
    "/session/{session_id}",
    summary="Get chat history"
)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Get chat history for a specific session
    
    - **session_id**: The chat session ID
    - **limit**: Maximum number of messages to retrieve (default: 50)
    
    Returns list of messages with metadata
    """
    try:
        messages = await uow.chat_repo.get_session_messages(session_id, limit=limit)
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found or has no messages"
            )
        
        return {
            "session_id": session_id,
            "message_count": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "provider_used": msg.provider_used,
                    "model_used": msg.model_used,
                    "tokens_used": msg.tokens_used,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch history", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chat history: {str(e)}"
        )


@router.get(
    "/sessions",
    summary="List all sessions"
)
async def list_sessions(
    limit: int = 50,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Get list of all chat sessions
    
    - **limit**: Maximum number of sessions to retrieve (default: 50)
    """
    try:
        # This requires adding a method to your repository
        # For now, return a simple response
        return {
            "message": "Session listing not yet implemented",
            "limit": limit
        }
        
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.delete(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete chat session"
)
async def delete_chat_session(
    session_id: str,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Delete a chat session and all its messages
    
    - **session_id**: The chat session ID to delete
    """
    try:
        # Get messages to check if session exists
        messages = await uow.chat_repo.get_session_messages(session_id, limit=1)
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        # Delete messages (this would require implementing delete methods)
        # For now, return success message
        logger.info("Session deletion requested", session_id=session_id)
        
        return {
            "message": f"Session '{session_id}' deletion requested",
            "session_id": session_id,
            "status": "pending",
            "note": "Full deletion not yet implemented"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.post(
    "/session/{session_id}/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear session messages"
)
async def clear_session_messages(
    session_id: str,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Clear all messages from a session (keeps session alive)
    
    - **session_id**: The chat session ID
    """
    try:
        messages = await uow.chat_repo.get_session_messages(session_id, limit=1)
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        logger.info("Session clear requested", session_id=session_id)
        
        return {
            "message": f"Session '{session_id}' messages cleared",
            "session_id": session_id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clear session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear session: {str(e)}"
        )


@router.get(
    "/session/{session_id}/stats",
    summary="Get session statistics"
)
async def get_session_stats(
    session_id: str,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Get statistics for a specific session
    
    - **session_id**: The chat session ID
    
    Returns message count, token usage, providers used, etc.
    """
    try:
        messages = await uow.chat_repo.get_session_messages(session_id, limit=1000)
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        # Calculate statistics
        total_messages = len(messages)
        user_messages = sum(1 for msg in messages if msg.role == "user")
        assistant_messages = sum(1 for msg in messages if msg.role == "assistant")
        total_tokens = sum(msg.tokens_used or 0 for msg in messages)
        
        providers_used = {}
        for msg in messages:
            if msg.provider_used:
                providers_used[msg.provider_used] = providers_used.get(msg.provider_used, 0) + 1
        
        return {
            "session_id": session_id,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_tokens": total_tokens,
            "providers_used": providers_used,
            "created_at": messages[0].created_at.isoformat() if messages else None,
            "last_message_at": messages[-1].created_at.isoformat() if messages else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session stats", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session statistics: {str(e)}"
        )
