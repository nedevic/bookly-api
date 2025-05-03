from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Book
from src.schemas.books_schemas import BookCreate, BookUpdate


class BookException(Exception):
    """Base class for BookService exceptions"""


class BookNotFoundException(BookException):
    def __init__(self, message: str = "Book was not found."):
        super().__init__(message)


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        books = result.all()
        return books

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        user_books = result.all()
        return user_books

    async def user_owns_book(self, user_uid: str, book_uid: str, session: AsyncSession):
        statement = select(Book).where(
            (Book.uid == book_uid) & (Book.user_uid == user_uid)
        )
        result = await session.exec(statement)
        user_book = result.first()
        return user_book is not None

    async def get_book(self, book_uid: str, session: AsyncSession):
        """
        Gets a book by book_uid. Raises BookNotFoundException if no book is found.
        """
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        if book:
            return book
        raise BookNotFoundException(f"Book with id {book_uid} was not found.")

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
        """
        Finds a book by book_uid and updates it. Raises BookNotFoundException if no book is found.
        """
        book_to_update = await self.get_book(book_uid, session)

        update_data_dict = update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(book_to_update, k, v)

        await session.commit()
        return book_to_update

    async def delete_book(self, book_uid: str, session: AsyncSession):
        """
        Finds a book by book_uid and deletes it. Raises BookNotFoundException if no book is found.
        """
        book_to_delete = await self.get_book(book_uid, session)
        await session.delete(book_to_delete)
        await session.commit()
        return book_to_delete
