import os
from fastapi import FastAPI
from app.db.init_db import create_db_and_tables
from app.handlers import user_handler, email_handler
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.handlers import shelter_handler
from app.handlers import disaster_handler
from app.services.region_service import load_region_csv
from app.services.shelter_service import fetch_and_store_shelters
from app.services.disaster_service import fetch_and_store_disasters
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Add routers
app.include_router(shelter_handler.router, prefix="/api", tags=["shelter"])
app.include_router(user_handler.router, prefix="/api", tags=["user"])
app.include_router(email_handler.router, prefix="/api", tags=["email"])  
app.include_router(disaster_handler.router, prefix="/api", tags=["disaster"])  
# DB setup
@app.on_event("startup")
async def on_startup():
    redis: Redis = await get_redis()
    await create_db_and_tables()
    await run_in_threadpool(fetch_and_store_shelters)
    await run_in_threadpool(fetch_and_store_disasters)
    await run_in_threadpool(load_region_csv)