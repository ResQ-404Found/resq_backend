FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip && \
    pip install "fastapi[standard]" \
    sqlmodel pymysql redis passlib[bcrypt] PyJWT requests pandas boto3 aiosmtplib cryptography apscheduler openai langchain langchain-openai firebase_admin bs4 google-api-python-client google-auth-httplib2 google-auth-oauthlib langchain-community chromadb

RUN pip install cryptography

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
