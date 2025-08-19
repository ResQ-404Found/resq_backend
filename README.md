# ResQ
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
pip install bs4
pip install google-api-python-client
pip install google-auth-httplib2
pip install google-auth-oauthlib
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
    HOSPITAL_API_SERVICE_KEY=your_hospital_api_key
    NAVER_CLIENT_ID = your_naver_client_id
    NAVER_CLIENT_SECRET = your_naver_client_secret
    YOUTUBE_API_KEY = your_youtube_api_key

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
│   │   ├── emergency_handler.py
│   │   ├── fcm_handler.py
│   │   ├── friend_handler.py
│   │   ├── hospital_handler.py
│   │   ├── like_handler.py
│   │   ├── news_handler.py
│   │   ├── notification_disastertype_handler.py
│   │   ├── notification_handler.py
│   │   ├── notification_region_handler.py
│   │   ├── post_handler.py
│   │   ├── purchase_handler.py
│   │   ├── shelter_handler.py
│   │   ├── sponsor_handler.py
│   │   ├── user_handler.py
│   │   └── youtube_handler.py
│   ├── models/
│   │   ├── chatbot_model.py
│   │   ├── comment_model.py
│   │   ├── disaster_model.py
│   │   ├── disaster_region_model.py
│   │   ├── emergency_model.py
│   │   ├── friend_model.py
│   │   ├── hospital_model.py
│   │   ├── like_model.py
│   │   ├── news_model.py
│   │   ├── notification_model.py
│   │   ├── post_model.py
│   │   ├── purchase_model.py
│   │   ├── region_model.py
│   │   ├── shelter_model.py
│   │   ├── sponsor_model.py
│   │   ├── user_model.py
│   │   └── youtube_model.py           
│   ├── schemas/
│   │   ├── chatbot_schema.py
│   │   ├── comment_schema.py
│   │   ├── common_schema.py
│   │   ├── disaster_schema.py
│   │   ├── email_schema.py
│   │   ├── emergency_schema.py
│   │   ├── friend_schema.py
│   │   ├── hospital_schema.py
│   │   ├── like_schema.py
│   │   ├── news_schema.py
│   │   ├── notification_disastertype_schema.py
│   │   ├── notification_region_schema.py
│   │   ├── notification_schema.py
│   │   ├── post_schema.py
│   │   ├── purchase_schema.py
│   │   ├── shelter_schema.py
│   │   ├── sponsor_schema.py
│   │   ├── user_schema.py
│   │   └── youtube_schema.py          
│   ├── services/
│   │   ├── chatbot_service.py
│   │   ├── comment_service.py
│   │   ├── disaster_region_service.py
│   │   ├── disaster_service.py
│   │   ├── email_service.py 
│   │   ├── emergency_service.py 
│   │   ├── fcm_service.py 
│   │   ├── friend_service.py 
│   │   ├── hospital_service.py
│   │   ├── like_service.py 
│   │   ├── news_service.py
│   │   ├── notification_disastertype_service.py 
│   │   ├── notification_region_service.py 
│   │   ├── notification_service.py 
│   │   ├── post_service.py
│   │   ├── purchase_service.py
│   │   ├── region_service.py
│   │   ├── shelter_service.py
│   │   ├── sponsor_service.py
│   │   ├── user_service.py
│   │   └── youtube_service.py   
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
- v4.0 4차 추가 기능 배포 완료 (병원, 뉴스AI, 유튜브 영상, 후원, 게시글 응답 구조 수정, 대댓글)
- v4.1 회원 탈퇴 후 로그인 에러 수정 및 FCM Test Handler 추가
- v4.2 게시글 type, Point 관련 수정
- v4.3 News 키워드 추출 및 기능 변경
- v4.4 Youtube API limit 추가, Post Delete Error Fix
- v4.5 CommentRead에 Author 필드 추가
- v4.6 Post 세부사항 수정(region id, comment count, sort)
- v5.0 비상 연락망/비상 알림 및 친구 기능 추가
```