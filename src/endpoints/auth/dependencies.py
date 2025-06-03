from typing import List

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.endpoints.auth.service import UserNotFoundException, UserService
from src.endpoints.auth.utils import decode_token
from src.redis.redis_jti import token_in_blocklist

user_service = UserService()


class TokenBearer(HTTPBearer):
    # def __init__(self, auto_error=True):  # auto_error should already be True
    #     super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)
        token_valid = token_data is not None

        if not token_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Invalid or expired token",
                    "resolution": "Please get a new token",
                },
            )

        return token_data


class AccessTokenBearer(TokenBearer):
    async def __call__(self, request: Request):
        token_data = await super().__call__(request)

        if token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Received a refresh token but expected an access token",
                    "resolution": "Please provide an access token",
                },
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked",
                    "resolution": "Please get a new token",
                },
            )

        return token_data


class RefreshTokenBearer(TokenBearer):
    async def __call__(self, request: Request):
        token_data = await super().__call__(request)

        if not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Received an access token but expected a refresh token",
                    "resolution": "Please provide a refresh token",
                },
            )

        return token_data


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    try:
        user_email = token_details["user"]["email"]
        return await user_service.get_user_by_email(user_email, session)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Missing or invalid email",
                "resolution": (
                    "Please make sure your user email is correct and up to date "
                    "or try to contact support"
                ),
            },
        )


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.role in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to perform this action",
            )
