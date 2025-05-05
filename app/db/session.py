import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()

MYSQL_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

db_engine = create_engine(MYSQL_URL, echo=True)

def get_db_session():
    with Session(db_engine) as session:
        yield session
