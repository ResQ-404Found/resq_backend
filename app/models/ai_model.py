import joblib
import os

# 모델 파일 경로 (기본은 /data 폴더)
MODEL_PATH = os.getenv("WILDFIRE_MODEL_PATH", "./data/wildfire_model.pkl")
ENCODER_PATH = os.getenv("LABEL_ENCODER_PATH", "./data/label_encoder.pkl")

# 미리 로드
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
