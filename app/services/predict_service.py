# -*- coding: utf-8 -*-
import os
import math
import requests
import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import torch
from dotenv import load_dotenv

# env 불러오기
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DISASTER_API_KEY = os.getenv("DISASTER_API_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# TorchScript 모델 로드
MODEL_PATH = os.path.join("data", "wildfire_model.ptl")
model = torch.jit.load(MODEL_PATH)
model.eval()

# ===============================
# 기상청 지점번호 매핑 (시·도 단위)
# ===============================
STN_MAP = {
    "서울": 108,
    "부산": 159,
    "대구": 143,
    "인천": 112,
    "광주": 156,
    "대전": 133,
    "울산": 152,
    "경기": 119,   # 수원
    "강원": 105,   # 춘천
    "충북": 131,   # 청주
    "충남": 129,   # 대전 대신
    "전북": 146,   # 전주
    "전남": 165,   # 목포
    "경북": 143,   # 대구
    "경남": 155,   # 진주
    "제주": 184    # 제주
}

# ===============================
# 외부 API
# ===============================
def get_weather(date: str, region: str):
    """기상청 시간자료 API (kma_sfctm2.php)"""
    stn = STN_MAP.get(region[:2], 108)  # 기본 서울=108
    tm = f"{date}0900"  # 하루 대표시각 = 09시

    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"
    params = {"tm": tm, "stn": stn, "authKey": WEATHER_API_KEY}
    r = requests.get(url, params=params, verify=False)

    if r.status_code != 200:
        return {"TA": 0, "RN_DAY": 0, "WS": 0}

    lines = r.text.strip().split("\n")
    for line in lines:
        if line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 15:
            continue
        try:
            return {
                "TA": float(parts[9]) if parts[9] not in [" ", "-", ""] else 0.0,     # 기온 (°C)
                "WS": float(parts[3]) if parts[3] not in [" ", "-", ""] else 0.0,     # 풍속 (m/s)
                "RN_DAY": float(parts[13]) if parts[13] not in [" ", "-", ""] else 0.0  # 일강수량 (mm)
            }
        except Exception:
            continue
    return {"TA": 0, "RN_DAY": 0, "WS": 0}


def get_disaster(date: str, region: str):
    """재난문자 API"""
    url = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"
    params = {
        "serviceKey": DISASTER_API_KEY,
        "pageNo": 1,
        "numOfRows": 100,
        "returnType": "xml",
        "crtDt": date,
    }
    r = requests.get(url, params=params, verify=False)
    if r.status_code != 200:
        return False

    try:
        root = ET.fromstring(r.text)
        items = root.findall(".//body/items/item")
    except ET.ParseError:
        return False

    if not items:
        return False

    rows = []
    for item in items:
        row = {c.tag: c.text for c in item}
        rows.append(row)
    df = pd.DataFrame(rows)

    return any(df["RCPTN_RGN_NM"].str.contains(region[:2], na=False))


def geocode_region(region: str):
    """카카오 주소 검색 API → 위도/경도"""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": region}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        docs = r.json().get("documents", [])
        if docs:
            return float(docs[0]["y"]), float(docs[0]["x"])
    return 0, 0

# ===============================
# 예측 함수
# ===============================
def predict_damage(region: str, use_yesterday: bool = True):
    if use_yesterday:
        target_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    else:
        target_date = datetime.date.today().strftime("%Y%m%d")

    weather = get_weather(target_date, region)
    disaster = get_disaster(target_date, region)

    X = torch.tensor([[weather["TA"], weather["RN_DAY"], weather["WS"], 1 if disaster else 0]],
                     dtype=torch.float32)

    pred = model(X).item()
    pred = max(pred, 0)  # 음수면 0으로 보정
    
    lat, lon = geocode_region(region)
    radius_m = math.sqrt((pred * 10000) / math.pi) if pred > 0 else 0

    return {
        "date": target_date,
        "region": region,
        "TA": weather["TA"],
        "RN_DAY": weather["RN_DAY"],
        "WS": weather["WS"],
        "message_exists": disaster,
        "lat": lat,
        "lon": lon,
        "pred_damage": float(pred),
        "pred_radius_m": radius_m,
    }
