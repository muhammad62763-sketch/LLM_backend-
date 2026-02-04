"""Admin API endpoints for system management and monitoring"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.presentation.api.dependencies import get_unit_of_work
from app.infrastructure.services.multi_api_service import multi_api_service
from app.core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/status",
    summary="Get system status"
)
async def get_system_status(
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Get overall system status including all API providers
    
    Returns provider availability, rate limits, and usage statistics
    """
    try:
        # Get provider status from rate limiter
        provider_status = multi_api_service.get_all_status()
        
        providers = []
        for name, status_info in provider_status.items():
            providers.append({
                "name": name,
                "available": status_info["available"],
                "minute_requests": status_info["minute_requests"],
                "minute_tokens": status_info["minute_tokens"],
                "day_tokens": status_info["day_tokens"],
                "last_error": status_info.get("last_error"),
                "limits": status_info["limits"]
            })
        
        # Get today's total usage from database
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            total_usage = await uow.usage_repo.get_total_usage(since=today)
            total_requests = total_usage.get("total_requests", 0)
            total_tokens = total_usage.get("total_tokens", 0)
        except Exception as e:
            logger.warning("Could not fetch usage stats", error=str(e))
            total_requests = 0
            total_tokens = 0
        
        return {
            "providers": providers,
            "total_requests_today": total_requests,
            "total_tokens_today": total_tokens,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system status: {str(e)}"
        )


@router.get(
    "/usage",
    summary="Get usage statistics"
)
async def get_usage_stats(
    hours: int = 24,
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Get usage statistics for the specified time period
    
    - **hours**: Number of hours to look back (default: 24)
    """
    try:
        since = datetime.now() - timedelta(hours=hours)
        
        # Get total usage
        total_usage = await uow.usage_repo.get_total_usage(since=since)
        
        # Get per-provider stats
        provider_stats = []
        for provider in multi_api_service.providers:
            try:
                stats = await uow.usage_repo.get_provider_stats(
                    provider_name=provider.name,
                    since=since
                )
                provider_stats.append({
                    "provider_name": provider.name,
                    **stats
                })
            except Exception as e:
                logger.warning(f"Could not get stats for {provider.name}", error=str(e))
                provider_stats.append({
                    "provider_name": provider.name,
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_tokens": 0,
                    "average_response_time": 0.0
                })
        
        return {
            "period_hours": hours,
            "start_time": since.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_requests": total_usage.get("total_requests", 0),
            "total_tokens": total_usage.get("total_tokens", 0),
            "average_response_time": total_usage.get("avg_response_time", 0.0),
            "provider_stats": provider_stats
        }
        
    except Exception as e:
        logger.error("Failed to get usage stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage statistics: {str(e)}"
        )


@router.get(
    "/providers",
    summary="List all providers"
)
async def list_providers() -> Dict[str, Any]:
    """
    Get list of all configured API providers
    """
    try:
        providers = []
        for provider in multi_api_service.providers:
            providers.append({
                "name": provider.name,
                "models": provider.models,
                "limits": {
                    "rpm": provider.rpm_limit,
                    "tpm": provider.tpm_limit,
                    "tpd": provider.tpd_limit
                }
            })
        
        return {
            "count": len(providers),
            "providers": providers
        }
        
    except Exception as e:
        logger.error("Failed to list providers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list providers: {str(e)}"
        )


@router.post(
    "/providers/{provider_name}/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset provider availability"
)
async def reset_provider(provider_name: str) -> Dict[str, Any]:
    """
    Manually reset a provider's availability status
    
    Useful when a provider was marked unavailable but should be retried
    """
    try:
        # Check if provider exists
        provider_exists = any(
            p.name == provider_name 
            for p in multi_api_service.providers
        )
        
        if not provider_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider_name}' not found"
            )
        
        multi_api_service.rate_limiter.mark_available(provider_name)
        
        logger.info("Provider reset", provider=provider_name)
        
        return {
            "message": f"Provider '{provider_name}' has been reset",
            "provider": provider_name,
            "status": "available",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to reset provider", provider=provider_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset provider: {str(e)}"
        )


@router.get(
    "/health",
    summary="Detailed health check"
)
async def detailed_health_check(
    uow: IUnitOfWork = Depends(get_unit_of_work)
) -> Dict[str, Any]:
    """
    Detailed health check including database and providers
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        await uow.usage_repo.get_total_usage(since=today)
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check providers
    provider_status = multi_api_service.get_all_status()
    available_count = sum(1 for p in provider_status.values() if p["available"])
    total_count = len(provider_status)
    
    health_status["components"]["providers"] = {
        "available": available_count,
        "total": total_count,
        "status": "healthy" if available_count > 0 else "unhealthy"
    }
    
    if available_count == 0:
        health_status["status"] = "unhealthy"
    
    return health_status
