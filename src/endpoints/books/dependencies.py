from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.endpoints.auth.dependencies import AccessTokenBearer
from src.endpoints.auth.utils import UserRoles
from src.endpoints.books.service import BookService

book_service = BookService()


async def owns_book_or_admin(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(AccessTokenBearer()),
):
    user_id = token_details["user"]["user_uid"]
    user_role = token_details["user"]["role"]
    if (
        not user_role == UserRoles.ADMIN.value
        and not await book_service.user_owns_book(user_id, book_id, session)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )
