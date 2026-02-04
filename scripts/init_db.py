import asyncio
from app.infrastructure.database.connection import db_manager, Base
from app.infrastructure.database.models import *

async def init_database():
    print("Initializing database...")
    engine = db_manager.create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized!")
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(init_database())
