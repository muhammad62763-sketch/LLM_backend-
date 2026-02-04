from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import httpx
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAPIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 60.0
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        pass
    
    @abstractmethod
    def _format_request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """Format request payload"""
        pass
    
    @abstractmethod
    def _parse_response(self, response_data: Dict) -> Dict:
        """Parse response data"""
        pass
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """Send chat completion request"""
        
        headers = self._get_headers()
        payload = self._format_request(messages, model, temperature, max_tokens)
        
        logger.info(
            "Sending API request",
            base_url=self.base_url,
            model=model
        )
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            return self._parse_response(response_data)
