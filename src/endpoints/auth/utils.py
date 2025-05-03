import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum

import jwt
from passlib.context import CryptContext

from src.endpoints.auth.config import settings

ACCESS_TOKEN_EXPIRY = 60 * 60  # 1 hour
REFRESH_TOKEN_EXPIRY = 60 * 60 * 24 * 2  # 2 days


class UserRoles(Enum):
    ADMIN = "admin"
    USER = "user"


passwd_context = CryptContext(
    schemes=["bcrypt"],
)


def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)


def verify_password(password: str, hash_: str):
    return passwd_context.verify(password, hash_)


def create_access_token(
    user_data: dict,
    refresh: bool = False,
):
    expiry = timedelta(
        seconds=(REFRESH_TOKEN_EXPIRY if refresh else ACCESS_TOKEN_EXPIRY)
    )
    payload = {
        "user": user_data,
        "exp": datetime.now() + expiry,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(
        payload=payload,
        key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            # options={
            #     "verify_exp": True,  # this should be enabled by default
            # }
        )
        return token_data
    except (jwt.PyJWKError, jwt.ExpiredSignatureError) as e:
        logging.exception(
            msg="An error occured when decoding the jwt token.",
            extra={
                "token": token,
                "error": e,
            },
        )
        return None


def create_access_token_pair_from_user_data(user_data: dict) -> dict:
    access_token = create_access_token(user_data=user_data)
    refresh_token = create_access_token(user_data=user_data, refresh=True)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "access_exp": ACCESS_TOKEN_EXPIRY,
        "refresh_exp": REFRESH_TOKEN_EXPIRY,
    }
