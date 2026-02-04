from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.application.dto.schemas import HealthResponse
from app.presentation.api.dependencies import get_db_session
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health check"
)
async def health_check(
    session: AsyncSession = Depends(get_db_session)
):
    """
    Check application health status
    
    Verifies:
    - Application is running
    - Database connection is working
    """
    try:
        # Test database connection
        result = await session.execute(text("SELECT 1"))
        db_status = "connected" if result else "disconnected"
        
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            database=db_status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            database="disconnected",
            timestamp=datetime.now().isoformat()
        )


@router.get(
    "/ready",
    summary="Readiness check"
)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    
    Returns 200 if the application is ready to serve traffic
    """
    return {"status": "ready"}


@router.get(
    "/live",
    summary="Liveness check"
)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    
    Returns 200 if the application is alive
    """
    return {"status": "alive"}
