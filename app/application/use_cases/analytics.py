"""Analytics use cases"""

from datetime import datetime, timedelta
from typing import List, Dict
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsUseCase:
    """Use case for analytics and reporting"""
    
    async def get_usage_report(
        self,
        uow: IUnitOfWork,
        hours: int = 24
    ) -> Dict:
        """Get comprehensive usage report"""
        logger.info("Generating usage report", hours=hours)
        
        since = datetime.now() - timedelta(hours=hours)
        
        # Get total usage
        total_usage = await uow.usage_repo.get_total_usage(since=since)
        
        # Get per-provider stats (you'll need to add this method)
        # For now, return basic stats
        return {
            "period_hours": hours,
            "total_requests": total_usage["total_requests"],
            "total_tokens": total_usage["total_tokens"],
            "start_time": since.isoformat(),
            "end_time": datetime.now().isoformat()
        }
    
    async def get_provider_comparison(
        self,
        uow: IUnitOfWork,
        hours: int = 24
    ) -> List[Dict]:
        """Compare all providers"""
        logger.info("Generating provider comparison", hours=hours)
        
        since = datetime.now() - timedelta(hours=hours)
        
        # This would iterate through all providers
        # For now, return empty list
        return []
