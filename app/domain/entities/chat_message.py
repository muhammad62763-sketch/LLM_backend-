from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Domain entity for chat messages"""
    
    session_id: str
    role: MessageRole
    content: str
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Message content cannot be empty")
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())
