import os
import requests
from sqlmodel import Session
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from datetime import datetime
from dotenv import load_dotenv
import urllib3
from app.services.disaster_region_service import parse_region_tuples, save_disaster_regions

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
            # 지역명 파싱
            try:
                region_str = item.get("RCPTN_RGN_NM", "")
                region_name = region_str.strip()
                region_tuples = parse_region_tuples(region_str, session)
            except Exception as e:
                print("Error parsing region:", e)
                continue
            # 재난 정보 저장
            try:
                disaster = DisasterInfo(
                    disaster_type=item.get("DST_SE_NM", "기타"),
                    disaster_level=item.get("EMRG_STEP_NM", "알수없음"),
                    info=item.get("MSG_CN", ""),
                    active=True,
                    start_time=datetime.strptime(item.get("CRT_DT"), "%Y/%m/%d %H:%M:%S"),
                    updated_at=datetime.utcnow(),
                    region_name=region_name
                )
                session.add(disaster)
                session.flush()
            except Exception as e:
                print("Error saving DisasterInfo:", e)
                continue
            # DisasterRegion 저장
            try:
                save_disaster_regions(session, disaster.id, region_tuples)
            except Exception as e:
                print("Error saving DisasterRegion:", e)
        try:
            session.commit()
        except Exception as e:
            print(f"[!] DB 저장 실패: {e}")
            session.rollback()
