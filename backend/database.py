import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

db_url = settings.database_url
if os.environ.get("VERCEL_ENV") or os.environ.get("VERCEL_URL"):
    db_url = "sqlite+aiosqlite:////tmp/monitoring.db"

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        from models import Monitor, Incident
        await conn.run_sync(Base.metadata.create_all)
