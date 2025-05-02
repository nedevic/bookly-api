from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookCreate, BookUpdate
from src.db.models import Book


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        return result.first()

    async def create_book(
        self, book_data: BookCreate, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        book_data_dict.update(
            {
                "published_date": datetime.strptime(
                    book_data_dict["published_date"],
                    "%Y-%m-%d",
                ),
                "user_uid": user_uid,
            }
        )
        new_book = Book(**book_data_dict)

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdate, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)
        if book_to_update is None:
            return None

        update_data_dict = update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(book_to_update, k, v)

        await session.commit()
        return book_to_update

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete is None:
            return None

        await session.delete(book_to_delete)
        await session.commit()
        return book_to_delete
