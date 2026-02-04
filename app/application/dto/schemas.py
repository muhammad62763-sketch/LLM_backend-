from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Request Schemas
class ChatRequest(BaseModel):
    """Request schema for chat messages"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(2000, ge=1, le=8000, description="Maximum tokens")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Explain quantum computing in simple terms",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
    )


# Response Schemas
class ChatResponse(BaseModel):
    """Response schema for chat messages"""
    session_id: str
    response: str
    provider_used: str
    model: str
    tokens_used: int
    response_time: float
    
    model_config = ConfigDict(from_attributes=True)


class ChatHistoryItem(BaseModel):
    """Single chat message in history"""
    role: str
    content: str
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""
    session_id: str
    messages: List[ChatHistoryItem]


class ProviderStatusResponse(BaseModel):
    """Provider status information"""
    name: str
    available: bool
    minute_requests: int
    minute_tokens: int
    day_tokens: int
    last_error: Optional[str] = None
    limits: dict


class SystemStatusResponse(BaseModel):
    """Overall system status"""
    providers: List[ProviderStatusResponse]
    total_requests_today: int
    total_tokens_today: int


class UsageStatsResponse(BaseModel):
    """Usage statistics for a provider"""
    provider_name: str
    total_requests: int
    successful_requests: int
    total_tokens: int
    average_response_time: float
    success_rate: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: str
