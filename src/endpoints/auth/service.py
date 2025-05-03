from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from src.endpoints.auth.utils import generate_passwd_hash
from src.schemas.auth_schemas import UserCreate


class UserException(Exception):
    """Base class for UserService exceptions"""


class UserNotFoundException(UserException):
    def __init__(self, message: str = "User was not found."):
        super().__init__(message)


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        """
        Gets an user by email. Raises UserNotFoundException if no user is found.
        """
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        if user:
            return user
        raise UserNotFoundException(f"User with email {email} was not found.")

    async def user_exists(self, email: str, session: AsyncSession):
        try:
            await self.get_user_by_email(email, session)
            return True
        except UserNotFoundException:
            return False

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        user_data_dict.update(
            {
                "password_hash": generate_passwd_hash(user_data_dict.pop("password")),
                "role": "user",
            }
        )
        new_user = User(**user_data_dict)
        session.add(new_user)
        await session.commit()
        return new_user
