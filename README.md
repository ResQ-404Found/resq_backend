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
pip install requests
pip install pandas
pip install boto3
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
    SHELTER_API_SERVICE_KEY = 대피소 API 키
    DISASTER_API_SERVICE_KEY = 재난 API 키
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    AWS_REGION=ap-northeast-2
    AWS_S3_BUCKET_NAME=your_bucket_name


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
├── requirements.txt
├── Dockerfile 
├── docker-compose.yml 
├── .dockerignore
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── data/
│   └── RegionCategory.csv
│
├── app/
│   ├── core/
│   │   └── redis.py
│   ├── db/               
│   │   ├── session.py
│   │   └── init_db.py
│   ├── handlers/
│   │   ├── email_handler.py
│   │   ├── user_handler.py
│   │   ├── disaster_handler.py
│   │   ├── post_handler.py
│   │   └── shelter_handler.py
│   ├── models/
│   │   ├── region_model.py
│   │   ├── user_model.py
│   │   ├── disaster_model.py
│   │   ├── post_model.py
│   │   └── shelter_models.py           
│   ├── schemas/
│   │   ├── common_schema.py
│   │   ├── user_schema.py
│   │   ├── post_schema.py
│   │   └── shelter_schema.py          
│   ├── services/ 
│   │   ├── region_service.py
│   │   ├── email_service.py
│   │   ├── user_service.py
│   │   ├── disaster_service.py
│   │   ├── post_service.py
│   │   └── shelter_service.py   
│   └── utils/
│       ├── s3_util.py
│       ├── jwt_util.py
│       └── redis_util.py 
```

###개발 버전 관리
```
- v1.0 Project 초기 세팅 및 example code
- v1.1 로그인/회원가입 기능, 이메일 인증 기능, 대피소 관련 핸들러 추가
- v1.2 배포 환경 설정 및 1차 배포
```