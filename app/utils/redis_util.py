from redis.asyncio import Redis
from datetime import timedelta

async def mark_email_verified(redis: Redis, email: str, ttl_minutes: int = 10):
    await redis.setex(f"verified:{email}", timedelta(minutes=ttl_minutes), "1")

async def is_email_verified(redis: Redis, email: str) -> bool:
    return await redis.get(f"verified:{email}") == "1"

async def clear_email_verified(redis: Redis, email: str):
    await redis.delete(f"verified:{email}")
