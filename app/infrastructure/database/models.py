from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Index
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class ChatSessionModel(Base):
    """SQLAlchemy model for chat sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('ix_chat_sessions_created_at', 'created_at'),
    )


class ChatMessageModel(Base):
    """SQLAlchemy model for chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    provider_used = Column(String(50), nullable=True)
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_chat_messages_session_created', 'session_id', 'created_at'),
    )


class APIUsageModel(Base):
    """SQLAlchemy model for API usage tracking"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), nullable=False, index=True)
    model_name = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    response_time = Column(Float, default=0.0)
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('ix_api_usage_provider_created', 'provider_name', 'created_at'),
        Index('ix_api_usage_success_created', 'success', 'created_at'),
    )
