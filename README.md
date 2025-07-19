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
pip install aiosmtplib
pip install cryptography
pip install apscheduler
pip install openai
pip install langchain
pip install langchain-openai
pip install firebase_admin
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
    HOSPITAL_API_SERVICE_KEY= 병원 API 키
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret_key
    AWS_REGION=ap-northeast-2
    AWS_S3_BUCKET_NAME=your_bucket_name
    OPENAI_API_KEY=your_openai_api_key
    

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
├── secrets/
│   └── firebase_service_account.json
│
├── app/
│   ├── core/
│   │   ├── firebase.py
│   │   └── redis.py
│   ├── db/               
│   │   ├── session.py
│   │   └── init_db.py
│   ├── handlers/
│   │   ├── chatbot_handler.py
│   │   ├── comment_handler.py
│   │   ├── disaster_handler.py
│   │   ├── email_handler.py
│   │   ├── fcm_handler.py
│   │   ├── like_handler.py
│   │   ├── notification_disastertype_handler.py
│   │   ├── notification_handler.py
│   │   ├── notification_region_handler.py
│   │   ├── post_handler.py
│   │   ├── shelter_handler.py
│   │   ├── sponsor_handler.py
│   │   ├── hospital_handler.py
│   │   └── user_handler.py
│   ├── models/
│   │   ├── chatbot_model.py
│   │   ├── comment_model.py
│   │   ├── disaster_model.py
│   │   ├── disaster_region_model.py
│   │   ├── like_model.py
│   │   ├── notification_model.py
│   │   ├── post_model.py
│   │   ├── region_model.py
│   │   ├── shelter_model.py
│   │   ├── sponsor_model.py
│   │   └── user_model.py           
│   ├── schemas/
│   │   ├── chatbot_schema.py
│   │   ├── comment_schema.py
│   │   ├── common_schema.py
│   │   ├── disaster_schema.py
│   │   ├── email_schema.py
│   │   ├── like_schema.py
│   │   ├── notification_disastertype_schema.py
│   │   ├── notification_region_schema.py
│   │   ├── notification_schema.py
│   │   ├── post_schema.py
│   │   ├── shelter_schema.py
│   │   ├── sponsor_schema.py
│   │   └── user_schema.py          
│   ├── services/
│   │   ├── chatbot_service.py
│   │   ├── comment_service.py
│   │   ├── disaster_region_service.py
│   │   ├── disaster_service.py
│   │   ├── email_service.py 
│   │   ├── fcm_service.py 
│   │   ├── like_service.py 
│   │   ├── notification_disastertype_service.py 
│   │   ├── notification_region_service.py 
│   │   ├── notification_service.py 
│   │   ├── post_service.py
│   │   ├── region_service.py
│   │   ├── shelter_service.py
│   │   ├── sponsor_service.py
│   │   └── user_service.py   
│   └── utils/
│       ├── fcm_util.py
│       ├── jwt_util.py
│       ├── redis_util.py
│       └── s3_util.py 
```

### 개발 버전 관리
```
- v1.0 Project 초기 세팅 및 example code
- v1.1 로그인/회원가입 기능, 이메일 인증 기능, 대피소 관련 핸들러 추가
- v1.2 배포 환경 설정 및 1차 배포
- v2.0 2차 배포 완료 (댓글, 재난정보, 게시글, 좋아요, 지역)
- v2.1 2차 추가 기능 배포 완료 (게시글 이미지 관련 기능)
- v3.0 3차 추가 기능 배포 완료 (알림, 챗봇, 스케쥴링)
```