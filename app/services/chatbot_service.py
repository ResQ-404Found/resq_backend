import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from sqlmodel import Session, select

from app.models.chatbot_model import ChatLog
from sqlmodel import Session
from app.db.session import db_engine

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LangChain 구성
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 재난 대응 전문가 챗봇입니다. 질문에 정확하고 친절하게 대답하세요."),
    ("user", "{input}")
])
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo-0125")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

def get_chat_response(user_message: str) -> str:
    return chain.invoke({"input": user_message})

def save_chat_log(user_id: int, user_message: str, bot_response: str):
    log = ChatLog(
        user_id=user_id,
        user_message=user_message,
        bot_response=bot_response
    )
    with Session(db_engine) as session:
        session.add(log)
        session.commit()

def get_chat_logs(user_id: int):
    with Session(db_engine) as session:
        return session.exec(
            select(ChatLog)
            .where(ChatLog.user_id == user_id)
            .order_by(ChatLog.created_at.desc())
            .limit(20)
        ).all()
