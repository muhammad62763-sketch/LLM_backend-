from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import db_manager
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.application.interfaces.unit_of_work import IUnitOfWork


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async for session in db_manager.get_session():
        yield session


async def get_unit_of_work(
    session: AsyncSession = Depends(get_db_session)
) -> IUnitOfWork:
    """FastAPI dependency for Unit of Work"""
    return UnitOfWork(session)
