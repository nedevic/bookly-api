from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.endpoints.auth.dependencies import get_current_user
from src.endpoints.reviews.schemas import Review, ReviewCreate
from src.endpoints.reviews.service import ReviewService

review_router = APIRouter()
review_service = ReviewService()


@review_router.post(
    "/book/{book_uid}", status_code=status.HTTP_201_CREATED, response_model=Review
)
async def add_review_for_book(
    book_uid: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_for_book(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )
    return new_review
