from fastapi import HTTPException, Depends
from sqlmodel import Session
from app.models.user_model import User
from app.utils.jwt_util import JWTUtil
from app.db.session import get_db_session
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import os
from app.utils.redis_util import mark_email_verified
from redis.asyncio import Redis
from app.core.redis import get_redis

class BaseSMTPClient:
    def send_email(self, to_email: str, subject: str, body: str):
        raise NotImplementedError

class GmailSMTPClient(BaseSMTPClient):
    def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = Header(subject)
        msg["From"] = os.getenv("GOOGLE_SMTP_EMAIL")
        msg["To"] = to_email
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.getenv("GOOGLE_SMTP_EMAIL"), os.getenv("GOOGLE_SMTP_PASSWORD"))
            smtp.sendmail(msg["From"], to_email, msg.as_string())

class EmailService:
    def __init__(self, db: Session=Depends(get_db_session), redis: Redis=Depends(get_redis)):
        self.db = db
        self.redis = redis
    
    async def request_verification(self, email: str, provider: str):
        if self.db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="이미 가입된 이메일 입니다.")
        
        token = JWTUtil.generate_email_verification_token(email)
        url = f"http://localhost:8000/api/verify-email?token={token}"
        self._send_email(email, url, provider)

    async def verify_email_token(self, token: str):
        try:
            email = JWTUtil.decode_email_verification_token(token)
        except Exception:
            raise HTTPException(status_code=400, detail="예상하지 못한 오류")
        await mark_email_verified(self.redis, email) 

    def _get_smtp_client(self, provider: str) -> BaseSMTPClient:
        if provider == "google":
            return GmailSMTPClient()
        else:
            raise ValueError("지원하지 않는 이메일 제공자입니다.")

    def _send_email(self, to_email: str, verify_url: str, provider: str):
            subject = "ResQ 이메일 인증"
            body = f"""
            <html>
                <body>
                    <h1>이메일 인증</h1>
                    <p>아래 링크를 클릭하여 이메일 인증을 완료하세요.</p>
                    <a href="{verify_url}">이메일 인증하기</a>
                </body>
            </html>
            """
            smtp_client = self._get_smtp_client(provider)
            smtp_client.send_email(to_email, subject, body)


