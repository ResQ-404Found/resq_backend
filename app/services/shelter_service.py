# app/services/shelter_service.py
import os
import requests
import urllib3
from datetime import datetime
from dotenv import load_dotenv
from sqlmodel import Session, select
from app.db.session import db_engine
from app.models.shelter_models import Shelter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(dotenv_path=".env")

def fetch_shelters():
    print(f"[INFO] Shelter Fetch 시작 : {datetime.utcnow()}")
    API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-10941"
    API_KEY = os.getenv("SHELTER_API_SERVICE_KEY")
    params = {
        "serviceKey": API_KEY,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "1000"
    }
    try:
        response = requests.get(API_URL, params=params)
    except Exception as e:
        print(f"[ERROR] Shelter API 요청 실패: {e}")
        return
    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] JSON parsing error: {e}")
        return []
    
    items = data.get("body", [])
    return items


def store_shelters(items: list):
    if not items:
        print("[INFO] No shelter data to store.")
        return
    
    with Session(db_engine) as session:
        for item in items:
            try:
                management_sn = item.get("MNG_SN")
                existing = session.exec(
                    select(Shelter).where(Shelter.management_serial_number == management_sn)
                ).first()
                if existing:
                    continue;
                
                shelter = Shelter(
                    facility_name=item.get("REARE_NM"),
                    road_address=item.get("RONA_DADDR"),
                    latitude=float(item.get("LAT", 0)),
                    longitude=float(item.get("LOT", 0)),
                    shelter_type_code=int(item.get("SHLT_SE_CD", 0)),
                    shelter_type_name=item.get("SHLT_SE_NM"),
                    management_serial_number=item.get("MNG_SN")
                )
                session.add(shelter)
            except Exception as e:
                print("[ERROR] Error adding shelter:", item.get("REARE_NM"), "->", e)
        session.commit()

def fetch_and_store_shelters():
    items = fetch_shelters()
    store_shelters(items)