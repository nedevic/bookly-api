from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Review
from src.endpoints.auth.service import UserException, UserService
from src.endpoints.books.service import BookException, BookService
from src.schemas.reviews_schemas import ReviewCreate

book_service = BookService()
user_service = UserService()


class ReviewException(Exception):
    """Base class for ReviewService exceptions"""

    def __init__(self, message: str):
        super().__init__(message)


class ReviewService:
    async def add_review_for_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreate,
        session: AsyncSession,
    ):
        """
        Adds a review for a book. Raises ReviewException if not successful.
        """
        try:
            book = await book_service.get_book(book_uid, session)
            user = await user_service.get_user_by_email(user_email, session)
        except (BookException, UserException):
            raise ReviewException(
                "Book or user couldn't be found. "
                f"Book id: {book_uid}  -  User email: {user_email}"
            )

        review_data_dict = review_data.model_dump()
        review_data_dict.update(
            {
                "user": user,
                "book": book,
            }
        )
        new_review = Review(**review_data_dict)

        session.add(new_review)
        await session.commit()
        return new_review
