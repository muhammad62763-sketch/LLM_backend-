from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, field
from app.domain.entities.api_provider import APIProvider, ProviderUsageTracker
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Token-bucket based rate limiter for API providers"""
    
    def __init__(self):
        self.trackers: Dict[str, ProviderUsageTracker] = {}
    
    def register_provider(self, provider: APIProvider) -> None:
        """Register a provider for rate limiting"""
        if provider.name not in self.trackers:
            self.trackers[provider.name] = ProviderUsageTracker(provider=provider)
            logger.info("Provider registered", provider=provider.name)
    
    def can_make_request(
        self,
        provider_name: str,
        estimated_tokens: int
    ) -> bool:
        """Check if request can be made within rate limits"""
        tracker = self.trackers.get(provider_name)
        if not tracker:
            return False
        
        self._reset_counters(tracker)
        
        provider = tracker.provider
        
        # Check RPM
        if tracker.minute_requests >= provider.rpm_limit:
            logger.warning(
                "RPM limit reached",
                provider=provider_name,
                current=tracker.minute_requests,
                limit=provider.rpm_limit
            )
            return False
        
        # Check TPM
        if tracker.minute_tokens + estimated_tokens > provider.tpm_limit:
            logger.warning(
                "TPM limit reached",
                provider=provider_name,
                current=tracker.minute_tokens,
                limit=provider.tpm_limit
            )
            return False
        
        # Check TPD
        if tracker.day_tokens + estimated_tokens > provider.tpd_limit:
            logger.warning(
                "Daily token limit reached",
                provider=provider_name,
                current=tracker.day_tokens,
                limit=provider.tpd_limit
            )
            return False
        
        return True
    
    def record_usage(
        self,
        provider_name: str,
        tokens_used: int
    ) -> None:
        """Record token usage after successful request"""
        tracker = self.trackers.get(provider_name)
        if not tracker:
            return
        
        tracker.minute_tokens += tokens_used
        tracker.day_tokens += tokens_used
        tracker.minute_requests += 1
        
        logger.debug(
            "Usage recorded",
            provider=provider_name,
            tokens=tokens_used,
            minute_total=tracker.minute_tokens,
            day_total=tracker.day_tokens
        )
    
    def mark_unavailable(
        self,
        provider_name: str,
        error: str
    ) -> None:
        """Mark provider as temporarily unavailable"""
        tracker = self.trackers.get(provider_name)
        if tracker:
            tracker.is_available = False
            tracker.last_error = error
            logger.warning("Provider marked unavailable", provider=provider_name, error=error)
    
    def mark_available(self, provider_name: str) -> None:
        """Mark provider as available"""
        tracker = self.trackers.get(provider_name)
        if tracker:
            tracker.is_available = True
            tracker.last_error = None
            logger.info("Provider marked available", provider=provider_name)
    
    def get_status(self, provider_name: str) -> Optional[Dict]:
        """Get current status of a provider"""
        tracker = self.trackers.get(provider_name)
        if not tracker:
            return None
        
        return {
            "available": tracker.is_available,
            "minute_requests": tracker.minute_requests,
            "minute_tokens": tracker.minute_tokens,
            "day_tokens": tracker.day_tokens,
            "last_error": tracker.last_error,
            "limits": {
                "rpm": tracker.provider.rpm_limit,
                "tpm": tracker.provider.tpm_limit,
                "tpd": tracker.provider.tpd_limit
            }
        }
    
    def _reset_counters(self, tracker: ProviderUsageTracker) -> None:
        """Reset time-based counters"""
        now = datetime.now()
        
        # Reset minute counters
        if (now - tracker.minute_start).total_seconds() >= 60:
            tracker.minute_tokens = 0
            tracker.minute_requests = 0
            tracker.minute_start = now
        
        # Reset day counters
        if (now - tracker.day_start).days >= 1:
            tracker.day_tokens = 0
            tracker.day_start = now
