import redis.asyncio as redis
from src.redis.config import settings

JTI_EXPIRY = 60 * 60  # 1 hour; corresponds to ACCESS_TOKEN_EXPIRY from src.auth.utils


token_blocklist = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
    db=0,
)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY,
    )


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    return jti is not None
