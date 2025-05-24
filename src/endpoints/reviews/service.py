from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Review
from src.endpoints.auth.service import UserException, UserService
from src.endpoints.books.service import BookException, BookService
from src.schemas.reviews_schemas import ReviewCreate, ReviewUpdate

book_service = BookService()
user_service = UserService()


class ReviewException(Exception):
    """Base class for ReviewService exceptions"""

    def __init__(self, message: str):
        super().__init__(message)


class ReviewNotFoundException(ReviewException):
    def __init__(self, message: str = "Review was not found."):
        super().__init__(message)


class ReviewService:
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        reviews = result.all()
        return reviews

    async def get_user_reviews(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Review)
            .where(Review.user_uid == user_uid)
            .order_by(desc(Review.created_at))
        )
        result = await session.exec(statement)
        user_reviews = result.all()
        return user_reviews

    async def get_review(self, review_uid: str, session: AsyncSession):
        """
        Gets a review by review_uid. Raises ReviewNotFoundException if no review is found.
        """
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        review = result.first()
        if review:
            return review
        raise ReviewNotFoundException(f"Review with id {review_uid} was not found.")

    async def user_owns_review(
        self, user_uid: str, review_uid: str, session: AsyncSession
    ):
        statement = select(Review).where(
            (Review.uid == review_uid) & (Review.user_uid == user_uid)
        )
        result = await session.exec(statement)
        user_review = result.first()
        return user_review is not None

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

    async def update_review(
        self, review_uid: str, update_data: ReviewUpdate, session: AsyncSession
    ):
        """
        Finds a review by review_uid and updates it.
        Raises ReviewNotFoundException if no review is found.
        """
        review_to_update = await self.get_review(review_uid, session)

        update_data_dict = update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(review_to_update, k, v)

        await session.commit()
        return review_to_update

    async def delete_review(self, review_uid: str, session: AsyncSession):
        """
        Finds a review by review_uid and deletes it.
        Raises ReviewNotFoundException if no review is found.
        """
        review_to_delete = await self.get_review(review_uid, session)
        await session.delete(review_to_delete)
        await session.commit()
        return review_to_delete
