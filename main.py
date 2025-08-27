from sched import scheduler
from fastapi import FastAPI
from app.core.firebase import init_firebase
from app.db.init_db import create_db_and_tables
from app.handlers import fcm_handler, notification_disastertype_handler, notification_handler, notification_region_handler, quiz_handler, sponsor_handler, user_handler, email_handler
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
from app.handlers import chatbot_handler
from app.handlers import hospital_handler
from app.services.hospital_service import fetch_and_store_hospitals
from app.handlers import news_handler
from app.handlers import youtube_handler
from app.handlers import purchase_handler
from app.handlers import friend_handler
from app.handlers import emergency_handler
from app.handlers import quiz_handler

app = FastAPI()
scheduler = BackgroundScheduler()

app.include_router(emergency_handler.router, prefix="/api", tags=["Emergency"])
app.include_router(friend_handler.router, prefix="/api", tags= ["Friend"])
app.include_router(youtube_handler.router, prefix="/api", tags= ["youtube"])
app.include_router(news_handler.router, prefix="/api", tags= ["news"])
app.include_router(hospital_handler.router, prefix="/api", tags=["hospital"])
app.include_router(shelter_handler.router, prefix="/api", tags=["shelter"])
app.include_router(user_handler.router, prefix="/api", tags=["user"])
app.include_router(email_handler.router, prefix="/api", tags=["email"])
app.include_router(disaster_handler.router, prefix="/api", tags=["disaster"])
app.include_router(post_handler.router, prefix="/api", tags=["posts"])
app.include_router(comment_handler.router, prefix="/api", tags=["comments"])
app.include_router(like_handler.router, prefix="/api", tags=["likes"])
app.include_router(chatbot_handler.router, prefix="/api", tags=["chatbot"])
app.include_router(fcm_handler.router, prefix="/api", tags=["fcm"])
app.include_router(notification_region_handler.router, prefix="/api", tags=["notification_region"])
app.include_router(notification_disastertype_handler.router, prefix="/api", tags=["notification_disastertype"])
app.include_router(notification_handler.router, prefix="/api", tags=["notification"])
app.include_router(sponsor_handler.router, prefix="/api", tags=["sponsor"])
app.include_router(purchase_handler.router,prefix='/api',tags =["purchase"])
app.include_router(quiz_handler.router,prefix='/api',tags =["quiz"])
@scheduler.scheduled_job("interval", hours=1)
def scheduled_disaster_fetch():
    fetch_and_store_disasters()

@scheduler.scheduled_job("cron", day=1, hour=0, minute=0)
def scheduled_shelter_fetch():
    fetch_and_store_shelters()

@scheduler.scheduled_job("cron", day=1, hour=0, minute=0)
def scheduled_hospital_fetch():
    fetch_and_store_hospitals()

# DB setup
@app.on_event("startup")
async def on_startup():
    redis: Redis = await get_redis()
    init_firebase()
    await create_db_and_tables()
    await run_in_threadpool(load_region_csv)
    await run_in_threadpool(fetch_and_store_shelters)
    await run_in_threadpool(fetch_and_store_disasters)
    await run_in_threadpool(fetch_and_store_hospitals)
    scheduler.start()
    print("[APScheduler] Started!")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("[APScheduler] Shutdown complete!")