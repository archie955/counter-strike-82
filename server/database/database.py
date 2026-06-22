from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from utils.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.postgres_username}:{settings.postgres_password}@{settings.postgres_hostname}/{settings.postgres_name}"

Base = declarative_base()
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except:
            await db.rollback()
            raise
