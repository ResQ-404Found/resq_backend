from redis import asyncio as aioredis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"

async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)
