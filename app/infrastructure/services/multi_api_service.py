from typing import List, Dict, Optional
import time
import asyncio
from app.domain.entities.api_provider import APIProvider
from app.infrastructure.external.api_clients.base_client import BaseAPIClient
from app.infrastructure.external.api_clients.groq_client import GroqClient
from app.infrastructure.external.api_clients.openrouter_client import OpenRouterClient
from app.infrastructure.external.api_clients.cerebras_client import CerebrasClient
from app.infrastructure.external.rate_limiter import RateLimiter
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.core.config import settings
from app.core.logging import get_logger
from httpx import HTTPStatusError

logger = get_logger(__name__)


class MultiAPIService:
    """Service for managing multiple API providers with automatic failover"""
    
    def __init__(self):
        self.providers: List[APIProvider] = []
        self.clients: Dict[str, BaseAPIClient] = {}
        self.rate_limiter = RateLimiter()
        self.current_index = 0
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize all API providers and their clients"""
        
        providers_config = [
            {
                "name": "Groq",
                "api_key": settings.GROQ_API_KEY,
                "base_url": "https://api.groq.com/openai/v1",
                "rpm_limit": settings.GROQ_RPM,
                "tpm_limit": settings.GROQ_TPM,
                "tpd_limit": settings.GROQ_TPD,
                "models": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
                "client_class": GroqClient
            },
            {
                "name": "Cerebras",
                "api_key": settings.CEREBRAS_API_KEY,
                "base_url": "https://api.cerebras.ai/v1",
                "rpm_limit": settings.CEREBRAS_RPM,
                "tpm_limit": settings.CEREBRAS_TPM,
                "tpd_limit": settings.CEREBRAS_TPD,
                "models": ["llama3.1-8b", "llama3.1-70b"],
                "client_class": CerebrasClient
            },
            {
                "name": "OpenRouter",
                "api_key": settings.OPENROUTER_API_KEY,
                "base_url": "https://openrouter.ai/api/v1",
                "rpm_limit": settings.OPENROUTER_RPM,
                "tpm_limit": settings.OPENROUTER_TPM,
                "tpd_limit": settings.OPENROUTER_TPD,
                "models": [
                    "meta-llama/llama-3.1-8b-instruct",
                    "meta-llama/llama-3.3-70b-instruct"
                ],
                "client_class": OpenRouterClient
            },
            {
                "name": "Mistral",
                "api_key": settings.MISTRAL_API_KEY,
                "base_url": "https://api.mistral.ai/v1",
                "rpm_limit": 30,
                "tpm_limit": 10000,
                "tpd_limit": 500000,
                "models": ["mistral-small-latest", "mistral-large-latest"],
                "client_class": GroqClient  # Uses OpenAI-compatible format
            },
            {
                "name": "DeepSeek",
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": "https://api.deepseek.com/v1",
                "rpm_limit": 50,
                "tpm_limit": 20000,
                "tpd_limit": 1000000,
                "models": ["deepseek-chat", "deepseek-coder"],
                "client_class": GroqClient  # Uses OpenAI-compatible format
            }
        ]
        
        for config in providers_config:
            provider = APIProvider(
                name=config["name"],
                api_key=config["api_key"],
                base_url=config["base_url"],
                rpm_limit=config["rpm_limit"],
                tpm_limit=config["tpm_limit"],
                tpd_limit=config["tpd_limit"],
                models=config["models"]
            )
            
            self.providers.append(provider)
            self.clients[provider.name] = config["client_class"](
                api_key=provider.api_key,
                base_url=provider.base_url
            )
            self.rate_limiter.register_provider(provider)
            
            logger.info("Provider initialized", provider=provider.name)
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4 + 200
    
    def _get_next_available_provider(
        self,
        estimated_tokens: int
    ) -> Optional[APIProvider]:
        """Find next available provider using round-robin"""
        attempts = 0
        
        while attempts < len(self.providers):
            provider = self.providers[self.current_index]
            
            if self.rate_limiter.can_make_request(provider.name, estimated_tokens):
                logger.info("Selected provider", provider=provider.name)
                return provider
            
            self.current_index = (self.current_index + 1) % len(self.providers)
            attempts += 1
        
        logger.error("All providers exhausted")
        return None
    
    async def chat_completion(
        self,
        message: str,
        uow: IUnitOfWork,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
    ) -> Dict:
        """
        Send chat completion request with automatic provider failover
        
        Args:
            message: User message
            uow: Unit of Work for database operations
            model: Specific model to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            max_retries: Maximum retry attempts
        
        Returns:
            Dict containing response content, provider info, and usage stats
        """
        estimated_tokens = self._estimate_tokens(message)
        messages = [{"role": "user", "content": message}]
        
        for attempt in range(max_retries):
            provider = self._get_next_available_provider(estimated_tokens)
            
            if not provider:
                logger.warning("No available providers, waiting...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    # Reset all providers to available
                    for p in self.providers:
                        self.rate_limiter.mark_available(p.name)
                    continue
                raise Exception("All API providers exhausted")
            
            client = self.clients[provider.name]
            selected_model = model or provider.models[0]
            
            start_time = time.time()
            
            try:
                logger.info(
                    "Attempting request",
                    provider=provider.name,
                    model=selected_model,
                    attempt=attempt + 1
                )
                
                response = await client.chat_completion(
                    messages=messages,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response_time = time.time() - start_time
                
                # Extract usage
                usage = response.get("usage", {})
                tokens_used = usage.get("total_tokens", estimated_tokens)
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                
                # Record usage in rate limiter
                self.rate_limiter.record_usage(provider.name, tokens_used)
                
                # Record usage in database
                await uow.usage_repo.record_usage(
                    provider_name=provider.name,
                    model_name=selected_model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    response_time=response_time,
                    success=True
                )
                
                logger.info(
                    "Request successful",
                    provider=provider.name,
                    tokens=tokens_used,
                    response_time=f"{response_time:.2f}s"
                )
                
                return {
                    "content": response["content"],
                    "provider": provider.name,
                    "model": response.get("model", selected_model),
                    "tokens_used": tokens_used,
                    "response_time": response_time
                }
                
            except HTTPStatusError as e:
                response_time = time.time() - start_time
                
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit", provider=provider.name)
                    self.rate_limiter.mark_unavailable(provider.name, "Rate limit exceeded")
                    
                    await uow.usage_repo.record_usage(
                        provider_name=provider.name,
                        model_name=selected_model,
                        prompt_tokens=0,
                        completion_tokens=0,
                        response_time=response_time,
                        success=False,
                        error_message="Rate limit exceeded"
                    )
                else:
                    logger.error(
                        "HTTP error",
                        provider=provider.name,
                        status_code=e.response.status_code,
                        error=str(e)
                    )
                    
                    await uow.usage_repo.record_usage(
                        provider_name=provider.name,
                        model_name=selected_model,
                        prompt_tokens=0,
                        completion_tokens=0,
                        response_time=response_time,
                        success=False,
                        error_message=str(e)
                    )
                
                self.current_index = (self.current_index + 1) % len(self.providers)
                continue
                
            except Exception as e:
                response_time = time.time() - start_time
                logger.error("Request failed", provider=provider.name, error=str(e))
                
                self.rate_limiter.mark_unavailable(provider.name, str(e))
                
                await uow.usage_repo.record_usage(
                    provider_name=provider.name,
                    model_name=selected_model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    response_time=response_time,
                    success=False,
                    error_message=str(e)
                )
                
                continue
        
        raise Exception("All retry attempts failed across all providers")
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all providers"""
        return {
            provider.name: self.rate_limiter.get_status(provider.name)
            for provider in self.providers
        }


# Global service instance
multi_api_service = MultiAPIService()
