import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from sqlmodel import Session, select

from app.models.chatbot_model import ChatLog
from sqlmodel import Session
from app.db.session import db_engine
from app.rag.counseling.service import ask_counseling_bot
from app.rag.disaster.service import ask_disaster_bot

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_disaster_response(user_message: str) -> str:
    return ask_disaster_bot(user_message)

def get_counseling_response(user_message: str) -> str:
    return ask_counseling_bot(user_message)

def save_chat_log(user_id: int, user_message: str, bot_response: str, chatbot_type: str):
    log = ChatLog(
        user_id=user_id,
        user_message=user_message,
        bot_response=bot_response,
        chatbot_type=chatbot_type
    )
    with Session(db_engine) as session:
        session.add(log)
        session.commit()

def get_chat_logs(user_id: int, chatbot_type: str):
    with Session(db_engine) as session:
        return session.exec(
            select(ChatLog)
            .where(ChatLog.user_id == user_id)
            .where(ChatLog.chatbot_type == chatbot_type)
            .order_by(ChatLog.created_at.desc())
            .limit(20)
        ).all()
