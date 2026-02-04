"""Seed database with sample data"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.infrastructure.database.connection import db_manager
from app.infrastructure.database.models import ChatSessionModel, ChatMessageModel, APIUsageModel
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def seed_data():
    """Seed database with sample data"""
    logger.info("Seeding database with sample data...")
    
    # Initialize engine first
    db_manager.create_engine()
    
    async for session in db_manager.get_session():
        try:
            # Create sample sessions
            sessions = [
                ChatSessionModel(session_id="demo-session-001"),
                ChatSessionModel(session_id="demo-session-002")
            ]
            
            for sess in sessions:
                session.add(sess)
            
            # Create sample messages
            messages = [
                ChatMessageModel(
                    session_id="demo-session-001",
                    role="user",
                    content="What is artificial intelligence?",
                    created_at=datetime.now()
                ),
                ChatMessageModel(
                    session_id="demo-session-001",
                    role="assistant",
                    content="Artificial Intelligence (AI) refers to computer systems that can perform tasks that typically require human intelligence...",
                    provider_used="Groq",
                    model_used="llama-3.1-8b-instant",
                    tokens_used=128,
                    created_at=datetime.now()
                ),
                ChatMessageModel(
                    session_id="demo-session-002",
                    role="user",
                    content="Explain quantum computing",
                    created_at=datetime.now()
                ),
                ChatMessageModel(
                    session_id="demo-session-002",
                    role="assistant",
                    content="Quantum computing is a revolutionary approach to computation that leverages quantum mechanics principles...",
                    provider_used="Cerebras",
                    model_used="llama3.1-70b",
                    tokens_used=156,
                    created_at=datetime.now()
                )
            ]
            
            for msg in messages:
                session.add(msg)
            
            # Create sample usage records
            usage_records = [
                APIUsageModel(
                    provider_name="Groq",
                    model_name="llama-3.1-8b-instant",
                    prompt_tokens=50,
                    completion_tokens=78,
                    total_tokens=128,
                    response_time=1.23,
                    success=True,
                    created_at=datetime.now()
                ),
                APIUsageModel(
                    provider_name="Cerebras",
                    model_name="llama3.1-70b",
                    prompt_tokens=45,
                    completion_tokens=111,
                    total_tokens=156,
                    response_time=0.89,
                    success=True,
                    created_at=datetime.now()
                )
            ]
            
            for record in usage_records:
                session.add(record)
            
            await session.commit()
            
            logger.info("✅ Sample data seeded successfully!")
            logger.info(f"   - Created {len(sessions)} sessions")
            logger.info(f"   - Created {len(messages)} messages")
            logger.info(f"   - Created {len(usage_records)} usage records")
            
        except Exception as e:
            logger.error(f"❌ Error seeding data: {e}")
            await session.rollback()
            raise
    
    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
