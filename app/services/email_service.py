from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from app.models.user_model import User, UserStatus
from app.utils.jwt_util import JWTUtil
from app.db.session import get_db_session
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import os
from app.utils.redis_util import mark_email_verified
from redis.asyncio import Redis
from app.core.redis import get_redis

class GmailSMTPClient:
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
        self.smtp_client = GmailSMTPClient()
    
    async def request_verification(self, email: str):
        if self.db.exec(select(User).where(User.email == email, User.status == UserStatus.ACTIVE)).first():
            raise HTTPException(status_code=400, detail="이미 가입된 이메일 입니다.")
        
        token = JWTUtil.generate_email_verification_token(email)
        url = f"http://localhost:3000/verify-email?token={token}"
        self._send_email_for_verify(email, url)

    async def request_password_reset(self, email: str):
        user = self.db.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="가입되지 않은 이메일 입니다.")
        
        token = JWTUtil.generate_password_reset_token(email)
        url = f"http://localhost:3000/reset-password?token={token}"
        self._send_email_for_reset(email, url)

    async def verify_email_token(self, token: str):
        try:
            email = JWTUtil.decode_email_verification_token(token)
        except Exception:
            raise HTTPException(status_code=400, detail="예상하지 못한 오류")
        await mark_email_verified(self.redis, email)

    def _send_email_for_verify(self, to_email: str, verify_url: str):
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
            self.smtp_client.send_email(to_email, subject, body)
    
    def _send_email_for_reset(self, to_email: str, reset_url: str):
        subject = "ResQ 비밀번호 재설정"
        body = f"""
        <html>
            <body>
                <h1>비밀번호 재설정</h1>
                <p>아래 링크를 클릭하여 비밀번호를 재설정하세요.</p>
                <a href="{reset_url}">비밀번호 재설정하기</a>
            </body>
        </html>
        """
        self.smtp_client.send_email(to_email, subject, body)


