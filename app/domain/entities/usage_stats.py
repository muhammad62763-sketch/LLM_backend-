from dataclasses import dataclass
from datetime import datetime

@dataclass
class UsageStats:
    provider_name: str
    total_requests: int
    successful_requests: int
    total_tokens: int
    average_response_time: float
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
