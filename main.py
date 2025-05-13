from fastapi import FastAPI
from app.db.init_db import create_db_and_tables
from app.handlers import user_handler, email_handler
from app.core.redis import get_redis

app = FastAPI()

# Add routers
app.include_router(user_handler.router, prefix="/api", tags=["user"])
app.include_router(email_handler.router, prefix="/api", tags=["email"])  

# DB setup
@app.on_event("startup")
async def on_startup():
    redis: Redis = await get_redis()
    await redis.flushdb()
    await create_db_and_tables()