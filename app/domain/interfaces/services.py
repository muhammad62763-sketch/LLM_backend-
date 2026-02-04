"""Service interfaces for domain layer"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class IMultiAPIService(ABC):
    """Interface for multi-API service"""
    
    @abstractmethod
    async def chat_completion(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """Send chat completion request"""
        pass
    
    @abstractmethod
    def get_all_status(self) -> Dict:
        """Get status of all providers"""
        pass
