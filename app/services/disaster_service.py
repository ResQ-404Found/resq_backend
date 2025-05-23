import os
import requests
from sqlmodel import Session
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from datetime import datetime
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"

def fetch_and_store_disasters():
    API_KEY = os.getenv("DISASTER_API_SERVICE_KEY")
    params = {
        "serviceKey": API_KEY,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "100"
    }

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()
        print(response.json())
    except Exception as e:
        print("Failed to fetch or parse disaster data:", e)
        return

    items = data.get("body")
    if not isinstance(items, list):
        print("Unexpected API format: body is not a list")
        return

    with Session(db_engine) as session:
        for item in items:
            try:
                disaster = DisasterInfo(
                    disaster_type=item.get("DST_SE_NM", "기타"),
                    disaster_level=item.get("EMRG_STEP_NM", "알수없음"),
                    info=item.get("MSG_CN", ""),
                    active=True,
                    start_time=datetime.strptime(item.get("CRT_DT"), "%Y/%m/%d %H:%M:%S"),
                    updated_at=datetime.utcnow(),
                )
                session.add(disaster)
            except Exception as e:
                print("Error saving disaster:", e)
        try:
            session.commit()
        except Exception as e:
            print(f"[!] DB 저장 실패: {e}")
            session.rollback()

