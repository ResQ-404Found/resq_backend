from redis.asyncio import Redis
from datetime import timedelta

async def mark_email_verified(redis: Redis, email: str, ttl_minutes: int = 10):
    ttl_seconds = ttl_minutes * 60
    await redis.setex(f"verified:{email}", ttl_seconds, "1")

async def is_email_verified(redis: Redis, email: str) -> bool:
    return await redis.get(f"verified:{email}") == "1"

async def clear_email_verified(redis: Redis, email: str):
    await redis.delete(f"verified:{email}")

async def store_verification_code(redis: Redis, email: str, code: str, ttl_minutes: int = 5):
    ttl_seconds = ttl_minutes * 60
    await redis.setex(f"verification_code:{email}", ttl_seconds, code)

async def get_verification_code(redis: Redis, email: str) -> str:
    code = await redis.get(f"verification_code:{email}")
    return code

async def clear_verification_code(redis: Redis, email: str):
    await redis.delete(f"verification_code:{email}")
