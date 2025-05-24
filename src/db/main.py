from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.config import settings

engine = AsyncEngine(
    create_engine(
        url=settings.database_url,
        echo=True,
    )
)


# async def init_db():
#     async with engine.begin() as conn:
#         from src.db.models import Book, Review, User, Tag, BookTagLink

#         await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with Session() as session:
        yield session
