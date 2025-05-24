from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.endpoints.auth.dependencies import AccessTokenBearer, get_current_user
from src.endpoints.reviews.dependencies import owns_review_or_admin
from src.endpoints.reviews.service import (
    ReviewException,
    ReviewNotFoundException,
    ReviewService,
)
from src.schemas.reviews_schemas import Review, ReviewCreate, ReviewUpdate

review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()


@review_router.get("/", response_model=List[Review])
async def get_all_reviews(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    return await review_service.get_all_reviews(session)


@review_router.get("/user/{user_uid}", response_model=List[Review])
async def get_user_reviews(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    return await review_service.get_user_reviews(user_uid, session)


@review_router.get("/{review_id}", response_model=Review)
async def get_review(
    review_id: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    try:
        return await review_service.get_review(review_id, session)
    except ReviewNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@review_router.post(
    "/book/{book_uid}",
    status_code=status.HTTP_201_CREATED,
    response_model=Review,
)
async def add_review_for_book(
    book_uid: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await review_service.add_review_for_book(
            user_email=current_user.email,
            book_uid=book_uid,
            review_data=review_data,
            session=session,
        )
    except ReviewException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@review_router.patch("/{review_id}", response_model=Review)
async def update_review(
    review_id: str,
    review_update_data: ReviewUpdate,
    session: AsyncSession = Depends(get_session),
    _=Depends(owns_review_or_admin),
) -> dict:
    try:
        return await review_service.update_review(
            review_id, review_update_data, session
        )
    except ReviewNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    session: AsyncSession = Depends(get_session),
    _=Depends(owns_review_or_admin),
):
    try:
        await review_service.delete_review(review_id, session)
    except ReviewNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
