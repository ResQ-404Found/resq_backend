from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from app.models.user_model import User, UserStatus
from app.db.session import get_db_session

from email.mime.text import MIMEText
from email.header import Header
import os
import random
import string

from app.utils.redis_util import (
    mark_email_verified,
    store_verification_code,
    get_verification_code,
    clear_verification_code,
)
from redis.asyncio import Redis
from app.core.redis import get_redis

from aiosmtplib import SMTP

class GmailSMTPClient:
    async def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = Header(subject)
        msg["From"] = os.getenv("GOOGLE_SMTP_EMAIL")
        msg["To"] = to_email
        
        smtp = SMTP(
            hostname="smtp.gmail.com",
            port=465,
            use_tls=True,
        )
        await smtp.connect()
        await smtp.login(
            os.getenv("GOOGLE_SMTP_EMAIL"), os.getenv("GOOGLE_SMTP_PASSWORD")
        )
        await smtp.send_message(msg)
        await smtp.quit()

class EmailService:
    def __init__(self, db: Session=Depends(get_db_session), redis: Redis=Depends(get_redis)):
        self.db = db
        self.redis = redis
        self.smtp_client = GmailSMTPClient()
    
    # 이메일 인증 요청 - 인증 코드 발송
    async def request_verification(self, email: str):
        if self.db.exec(
            select(User).where(User.email == email, User.status == UserStatus.ACTIVE)
            ).first():
            raise HTTPException(status_code=400, detail="이미 가입된 이메일 입니다.")
        
        verification_code = self._generate_verification_code()
        await store_verification_code(self.redis, email, verification_code, ttl_minutes=5)
        await self._send_email_for_verify(email, verification_code)

    # 이메일 인증코드 검증
    async def verify_email_code(self, email: str, code: str):
        try:
            stored_code = await get_verification_code(self.redis, email)
            if not stored_code:
                raise HTTPException(status_code=400, detail="인증코드가 만료되었습니다. 다시 요청해주세요.")
            if code != stored_code:
                raise HTTPException(status_code=400, detail="인증코드가 일치하지 않습니다.")
            
            await mark_email_verified(self.redis, email)
            await clear_verification_code(self.redis, email)

        except Exception as e:
            print(f"오류 발생: {repr(e)}")
            raise HTTPException(status_code=400, detail="인증코드 검증 중 오류가 발생했습니다.")

    # 비밀번호 재설정 요청 - 인증코드 발송
    async def request_password_reset(self, email: str):
        user = self.db.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="가입되지 않은 이메일 입니다.")
        
        verification_code = self._generate_verification_code()
        await store_verification_code(self.redis, f"reset:{email}", verification_code, ttl_minutes=5)
        await self._send_email_for_reset(email, verification_code)

    # 비밀번호 재설정 인증코드 검증
    async def verify_password_reset_code(self, email: str, code: str):
        try:
            stored_code = await get_verification_code(self.redis, f"reset:{email}")
            if not stored_code:
                raise HTTPException(status_code=400, detail="인증코드가 만료되었습니다. 다시 요청해주세요.")
            if code != stored_code:
                raise HTTPException(status_code=400, detail="인증코드가 일치하지 않습니다.")
            
            await mark_email_verified(self.redis, f"reset:{email}")
            await clear_verification_code(self.redis, f"reset:{email}")
            
        except Exception as e:
            print(f"오류 발생: {repr(e)}")
            raise HTTPException(status_code=400, detail="인증코드 검증 중 오류가 발생했습니다.")

    async def _send_email_for_verify(self, to_email: str, verification_code: str):
        subject = "ResQ 이메일 인증"
        body = f"""
        <html>
            <body>
                <h1>이메일 인증</h1>
                <p>아래 인증코드를 입력하여 이메일 인증을 완료하세요.</p>
                <h2 style="color: #007bff; font-size: 24px; letter-spacing: 5px;">{verification_code}</h2>
                <p style="color: #666; font-size: 12px;">인증코드는 5분간 유효합니다.</p>
            </body>
        </html>
        """
        await self.smtp_client.send_email(to_email, subject, body)
    
    async def _send_email_for_reset(self, to_email: str, verification_code: str):
        subject = "ResQ 비밀번호 재설정"
        body = f"""
        <html>
            <body>
                <h1>비밀번호 재설정</h1>
                <p>아래 인증코드를 입력하여 비밀번호를 재설정하세요.</p>
                <h2 style="color: #007bff; font-size: 24px; letter-spacing: 5px;">{verification_code}</h2>
                <p style="color: #666; font-size: 12px;">인증코드는 5분간 유효합니다.</p>
            </body>
        </html>
        """
        await self.smtp_client.send_email(to_email, subject, body)

    # 인증코드 생성 (6자리 숫자)
    def _generate_verification_code(self) -> str:
        return ''.join(random.choices(string.digits, k=6))

