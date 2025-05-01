from pydantic import Field
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    redis_host: str = "redis"
    redis_port: str = Field(..., alias="REDIS_PORT")


settings = _Settings()
