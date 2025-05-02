from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    get_current_user,
)
from src.auth.schemas import User, UserCreate, UserLogin
from src.auth.service import UserService
from src.auth.utils import create_access_token_pair_from_user_data, verify_password
from src.db.main import get_session
from src.redis.redis_jti import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()


@auth_router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password.",
        )

    password_valid = verify_password(password, user.password_hash)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password.",
        )

    user_data = {
        "email": user.email,
        "user_uid": str(user.uid),
        "role": user.role,
    }
    access_token_pair = create_access_token_pair_from_user_data(user_data)
    return JSONResponse(content=access_token_pair)


@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: dict = Depends(refresh_token_bearer),
):
    user_data = token_details["user"]
    access_token_pair = create_access_token_pair_from_user_data(user_data)
    return JSONResponse(content=access_token_pair)


@auth_router.get("/logout")
async def revoke_token(
    token_details: dict = Depends(access_token_bearer),
):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Logged out successfully",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.get("/current_user")
async def get_user(user=Depends(get_current_user)):
    return user
