from sqlmodel import SQLModel
from app.db.session import db_engine

def create_db_and_tables():
    SQLModel.metadata.drop_all(db_engine)
    SQLModel.metadata.create_all(db_engine)