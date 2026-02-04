from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    """Domain entity for chat sessions"""
    session_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = None
    last_message_at: Optional[datetime] = None
