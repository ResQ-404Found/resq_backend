from sqlmodel import SQLModel, Session
from app.db.session import db_engine
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService

async def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)
