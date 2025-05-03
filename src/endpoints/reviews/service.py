from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Review
from src.endpoints.auth.service import UserService
from src.endpoints.books.service import BookService
from src.endpoints.reviews.schemas import ReviewCreate

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_for_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreate,
        session: AsyncSession,
    ):
        book = await book_service.get_book(book_uid, session)
        user = await user_service.get_user_by_email(user_email, session)

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
