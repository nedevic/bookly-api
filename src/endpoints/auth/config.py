from pydantic import Field
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(..., alias="JWT_ALGORITHM")


settings = _Settings()
