from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Engine síncrono (para scripts y create_all)
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", ""),
    echo=settings.debug,
)

# Engine asíncrono (para FastAPI)
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def create_db_and_tables():
    """Crea las tablas (usar solo en desarrollo / primer arranque)."""
    SQLModel.metadata.create_all(sync_engine)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session