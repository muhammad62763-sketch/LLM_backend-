from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class APIProvider:
    """Immutable domain entity representing an API provider"""
    
    name: str
    api_key: str
    base_url: str
    rpm_limit: int  # Requests per minute
    tpm_limit: int  # Tokens per minute
    tpd_limit: int  # Tokens per day
    models: List[str]
    request_format: str = "openai"
    
    def __post_init__(self) -> None:
        """Validate entity invariants"""
        if self.rpm_limit <= 0:
            raise ValueError("rpm_limit must be positive")
        if self.tpm_limit <= 0:
            raise ValueError("tpm_limit must be positive")
        if not self.models:
            raise ValueError("models list cannot be empty")


@dataclass
class ProviderUsageTracker:
    """Tracks usage for a specific provider"""
    
    provider: APIProvider
    minute_tokens: int = 0
    day_tokens: int = 0
    minute_requests: int = 0
    minute_start: datetime = None
    day_start: datetime = None
    is_available: bool = True
    last_error: Optional[str] = None
    
    def __post_init__(self) -> None:
        if self.minute_start is None:
            object.__setattr__(self, 'minute_start', datetime.now())
        if self.day_start is None:
            object.__setattr__(self, 'day_start', datetime.now())
