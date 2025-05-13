from fastapi import FastAPI
from app.db.init_db import create_db_and_tables

app = FastAPI()

# Add routers

# DB setup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()