FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "fastapi[standard]" \
    sqlmodel pymysql redis passlib[bcrypt] PyJWT requests pandas boto3 aiosmtplib cryptography apscheduler openai langchain langchain-openai firebase_admin bs4 google-api-python-client google-auth-httplib2 google-auth-oauthlib langchain-community chromadb pypdf joblib scikit-learn

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
