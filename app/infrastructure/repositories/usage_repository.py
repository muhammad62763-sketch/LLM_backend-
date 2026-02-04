from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories import IUsageRepository
from app.infrastructure.database.models import APIUsageModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class UsageRepository(IUsageRepository):
    """Implementation of usage repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_usage(
        self,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Record API usage"""
        logger.info(
            "Recording usage",
            provider=provider_name,
            model=model_name,
            tokens=prompt_tokens + completion_tokens,
            success=success
        )
        
        usage = APIUsageModel(
            provider_name=provider_name,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            response_time=response_time,
            success=success,
            error_message=error_message
        )
        
        self.session.add(usage)
        await self.session.flush()
    
    async def get_provider_stats(
        self,
        provider_name: str,
        since: datetime
    ) -> dict:
        """Get usage statistics for a provider"""
        stmt = select(
            func.count(APIUsageModel.id).label('total_requests'),
            func.sum(func.cast(APIUsageModel.success, Integer)).label('successful'),
            func.sum(APIUsageModel.total_tokens).label('total_tokens'),
            func.avg(APIUsageModel.response_time).label('avg_time')
        ).where(
            APIUsageModel.provider_name == provider_name,
            APIUsageModel.created_at >= since
        )
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        if not row or row.total_requests == 0:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'total_tokens': 0,
                'average_response_time': 0.0,
                'success_rate': 0.0
            }
        
        return {
            'total_requests': row.total_requests,
            'successful_requests': row.successful or 0,
            'total_tokens': row.total_tokens or 0,
            'average_response_time': float(row.avg_time or 0.0),
            'success_rate': (row.successful / row.total_requests * 100) if row.total_requests > 0 else 0.0
        }
    
    async def get_total_usage(self, since: datetime) -> dict:
        """Get total usage across all providers"""
        stmt = select(
            func.count(APIUsageModel.id).label('total_requests'),
            func.sum(APIUsageModel.total_tokens).label('total_tokens')
        ).where(
            APIUsageModel.created_at >= since
        )
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        return {
            'total_requests': row.total_requests or 0,
            'total_tokens': row.total_tokens or 0
        }
