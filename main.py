from sched import scheduler
from fastapi import FastAPI
from app.db.init_db import create_db_and_tables
from app.handlers import user_handler, email_handler
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.handlers import shelter_handler
from app.handlers import disaster_handler
from app.services.region_service import load_region_csv
from app.services.shelter_service import fetch_and_store_shelters
from app.services.disaster_service import fetch_and_store_disasters
from app.handlers import post_handler
from starlette.concurrency import run_in_threadpool
from app.handlers import comment_handler 
from app.handlers import like_handler


app = FastAPI()
scheduler = BackgroundScheduler()

# Add routers
app.include_router(shelter_handler.router, prefix="/api", tags=["shelter"])
app.include_router(user_handler.router, prefix="/api", tags=["user"])
app.include_router(email_handler.router, prefix="/api", tags=["email"])
app.include_router(disaster_handler.router, prefix="/api", tags=["disaster"])
#app.include_router(upload_test.router, prefix="/api", tags=["upload"])
app.include_router(post_handler.router, prefix="/api", tags=["posts"])
app.include_router(comment_handler.router, prefix="/api", tags=["comments"])
app.include_router(like_handler.router, prefix="/api", tags=["likes"])

@scheduler.scheduled_job("interval", hours=1)
def scheduled_disaster_fetch():
    fetch_and_store_disasters()

@scheduler.scheduled_job("cron", day=1, hour=0, minute=0)
def scheduled_shelter_fetch():
    fetch_and_store_shelters()

# DB setup
@app.on_event("startup")
async def on_startup():
    redis: Redis = await get_redis()
    await create_db_and_tables()
    await run_in_threadpool(load_region_csv)
    await run_in_threadpool(fetch_and_store_shelters)
    await run_in_threadpool(fetch_and_store_disasters)
    scheduler.start()
    print("[APScheduler] Started!")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("[APScheduler] Shutdown complete!")