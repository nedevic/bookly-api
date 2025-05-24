from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.endpoints.auth.dependencies import AccessTokenBearer
from src.endpoints.auth.utils import UserRoles
from src.endpoints.reviews.service import ReviewService

review_service = ReviewService()


async def owns_review_or_admin(
    review_id: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(AccessTokenBearer()),
):
    user_id = token_details["user"]["user_uid"]
    user_role = token_details["user"]["role"]
    if (
        not user_role == UserRoles.ADMIN.value
        and not await review_service.user_owns_review(user_id, review_id, session)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )
