from fastapi import FastAPI
from app.handlers.example import example_router
from app.db.init_db import create_db_and_tables

app = FastAPI()

# Add routers
app.include_router(example_router, prefix="/api")  

# DB setup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()