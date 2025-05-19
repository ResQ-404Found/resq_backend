import os
from fastapi import FastAPI
from app.db.init_db import create_db_and_tables
from app.handlers import user_handler, email_handler
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.handlers import shelter_handler
from app.services.shelter_service import fetch_and_store_shelters
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Add routers
app.include_router(shelter_handler.router, prefix="/api", tags=["shelter"])
app.include_router(user_handler.router, prefix="/api", tags=["user"])
app.include_router(email_handler.router, prefix="/api", tags=["email"])  

# DB setup
@app.on_event("startup")
async def on_startup():
    redis: Redis = await get_redis()
    await create_db_and_tables()
    await run_in_threadpool(fetch_and_store_shelters)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)