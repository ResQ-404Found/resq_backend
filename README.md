### 2025-Spring-Project-Backend
### team 404Found

### 개발환경 설치
```
가상환경 설정
python3 -m venv .venv

가상환경 활성화
.venv/Scripts/activate.bat

패키지 설치
pip install "fastapi[standard]"
pip install sqlmodel
pip install pymysql
pip install redis
pip install passlib[bcrypt]
pip install PyJWT
```

### .env file 
    DB_HOST=127.0.0.1
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_password
    DB_NAME=your_database
    REDIS_HOST=127.0.0.1
    REDIS_PORT=6379
    GOOGLE_SMTP_EMAIL=your_email
    GOOGLE_SMTP_PASSWORD=your_smtp_password

### Redis (Ubuntu,Linux)
    sudo apt install redis redis-tools -y
    
    Redis CLI 실행
    redis-cli

### FastAPI 서버 실행
    fastapi dev main.py

### 프로젝트 구조
```
project-root/
│        
├── README.md           
├── .env
├── .gitignore 
├── main.py              
│
├── app/
│   ├── core/
│   │   └── redis.py
│   ├── db/               
│   │   ├── session.py
│   │   └── init_db.py
│   ├── handlers/
│   │   ├── email_handler.py
│   │   └── user_handler.py
│   ├── models/
│   │   └── user_model.py           
│   ├── schemas/
│   │   ├── common_schema.py
│   │   └── user_schema.py          
│   ├── services/ 
│   │   ├── email_service.py
│   │   └── user_service.py   
│   └── utils/
│       ├── jwt_util.py
│       └── redis_util.py 

```