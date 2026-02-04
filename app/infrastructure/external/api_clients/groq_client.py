from typing import Dict, List
from app.infrastructure.external.api_clients.base_client import BaseAPIClient


class GroqClient(BaseAPIClient):
    """Groq API client implementation"""
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _format_request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict:
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    
    def _parse_response(self, response_data: Dict) -> Dict:
        return {
            "content": response_data["choices"][0]["message"]["content"],
            "model": response_data.get("model"),
            "usage": response_data.get("usage", {})
        }
