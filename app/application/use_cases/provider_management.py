"""Provider management use cases"""

from typing import List, Dict
from app.infrastructure.services.multi_api_service import multi_api_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProviderManagementUseCase:
    """Use case for managing API providers"""
    
    def __init__(self):
        self.multi_api_service = multi_api_service
    
    def get_all_providers(self) -> List[Dict]:
        """Get list of all available providers"""
        logger.info("Fetching all providers")
        
        return [
            {
                "name": provider.name,
                "models": provider.models,
                "limits": {
                    "rpm": provider.rpm_limit,
                    "tpm": provider.tpm_limit,
                    "tpd": provider.tpd_limit
                }
            }
            for provider in self.multi_api_service.providers
        ]
    
    def get_provider_status(self, provider_name: str) -> Dict:
        """Get status of a specific provider"""
        logger.info("Fetching provider status", provider=provider_name)
        
        status = self.multi_api_service.rate_limiter.get_status(provider_name)
        
        if not status:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        return status
    
    def reset_provider(self, provider_name: str) -> Dict:
        """Reset a provider's availability"""
        logger.info("Resetting provider", provider=provider_name)
        
        self.multi_api_service.rate_limiter.mark_available(provider_name)
        
        return {
            "provider": provider_name,
            "status": "reset_successful",
            "available": True
        }
