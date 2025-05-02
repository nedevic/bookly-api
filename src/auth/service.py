from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.utils import generate_passwd_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None

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
