"""
Database configuration — async SQLAlchemy engine with SQLite (aiosqlite).
Auto-creates eduscraper.db on startup.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eduscraper.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables and FTS5 virtual tables on startup."""
    from models import Base as ModelsBase  # noqa: F811

    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)
        # Create FTS5 virtual table for full-text search
        await conn.execute(
            __import__("sqlalchemy").text(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS faculty_fts USING fts5(
                    name, email, department, designation,
                    content='faculty_contacts',
                    content_rowid='id'
                )
                """
            )
        )


async def get_session() -> AsyncSession:
    """Dependency for FastAPI route injection."""
    async with async_session() as session:
        yield session
