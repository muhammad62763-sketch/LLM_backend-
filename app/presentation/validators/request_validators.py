"""Request validation utilities"""

from typing import Optional
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)


def validate_session_id(session_id: str) -> str:
    """Validate session ID format"""
    if not session_id or len(session_id) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    return session_id


def validate_message_content(content: str) -> str:
    """Validate message content"""
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )
    
    if len(content) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content exceeds maximum length of 10000 characters"
        )
    
    return content.strip()


def validate_temperature(temperature: float) -> float:
    """Validate temperature parameter"""
    if not 0.0 <= temperature <= 2.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temperature must be between 0.0 and 2.0"
        )
    return temperature


def validate_max_tokens(max_tokens: int) -> int:
    """Validate max_tokens parameter"""
    if not 1 <= max_tokens <= 8000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_tokens must be between 1 and 8000"
        )
    return max_tokens


def validate_provider_name(provider_name: str, valid_providers: list) -> str:
    """Validate provider name"""
    if provider_name not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found. Valid providers: {', '.join(valid_providers)}"
        )
    return provider_name
