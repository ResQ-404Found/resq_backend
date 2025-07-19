import os
import requests
import urllib3
from datetime import datetime
from dotenv import load_dotenv
from sqlmodel import Session, select
from app.db.session import db_engine
from app.models.hospital_model import Hospital, HospitalOperatingHour

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(dotenv_path=".env")

API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-10840"
API_KEY = os.getenv("HOSPITAL_API_SERVICE_KEY")

# 요일 및 공휴일 필드 매핑
DAY_MAPPINGS = {
    "월요일": ("MDEXM_HR_MNDY_C", "MDEXM_HR_MNDY_S"),
    "화요일": ("MDEXM_HR_TSDY_C", "MDEXM_HR_TSDY_S"),
    "수요일": ("MDEXM_HR_WDDY_C", "MDEXM_HR_WDDY_S"),
    "목요일": ("MDEXM_HR_THDY_C", "MDEXM_HR_THDY_S"),
    "금요일": ("MDEXM_HR_FRDY_C", "MDEXM_HR_FRDY_S"),
    "토요일": ("MDEXM_HR_STDY_C", "MDEXM_HR_STDY_S"),
    "일요일": ("MDEXM_HR_SNDY_C", "MDEXM_HR_SNDY_S"),
    "공휴일": ("MDEXM_HR_LHLDY_C", "MDEXM_HR_LHLDY_S"),
}


def fetch_hospitals():
    print(f"[INFO] 병원 데이터 Fetch 시작: {datetime.utcnow()}")

    params = {
        "serviceKey": API_KEY,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "5"
    }

    try:
        response = requests.get(API_URL, params=params, verify=False)
        print("[DEBUG] 최종 요청 URL:", response.request.url)
        print("[DEBUG] 응답 상태코드:", response.status_code)
        print("[DEBUG] 응답 내용 (앞부분):", response.text[:300])
    except Exception as e:
        print(f"[ERROR] 병원 API 요청 실패: {e}")
        return []

    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] JSON 파싱 실패: {e}")
        return []

    items = data.get("body", [])
    return items


def store_hospitals(items: list):
    if not items:
        print("[INFO] 저장할 병원 데이터가 없습니다.")
        return

    with Session(db_engine) as session:
        for item in items:
            try:
                name = item.get("INST_NM")
                address = item.get("ADDR")
                lat = float(item.get("HSPTL_LAT", 0))
                lon = float(item.get("HSPTL_LOT", 0))
                phone = item.get("RPRS_TLHN_1")
                emergency = item.get("EMRO_OPER_YN_", "N") == "Y"

                if not name or lat == 0 or lon == 0:
                    continue

                existing = session.exec(
                    select(Hospital).where(
                        Hospital.facility_name == name,
                        Hospital.road_address == address
                    )
                ).first()
                if existing:
                    continue

                hospital = Hospital(
                    facility_name=name,
                    road_address=address,
                    latitude=lat,
                    longitude=lon,
                    phone_number=phone,
                    emergency_room=emergency,
                    weekend_operating=None  # 안전데이터에서는 주말 운영 여부 명시 안 함
                )
                session.add(hospital)
                session.commit()
                session.refresh(hospital)

                # 진료시간 저장
                for day_name, (start_key, end_key) in DAY_MAPPINGS.items():
                    open_time = item.get(start_key)
                    close_time = item.get(end_key)
                    is_closed = (not open_time) and (not close_time)

                    hour = HospitalOperatingHour(
                        hospital_id=hospital.id,
                        day_of_week=day_name,
                        open_time=open_time if not is_closed else None,
                        close_time=close_time if not is_closed else None,
                        is_closed=is_closed
                    )
                    session.add(hour)

            except Exception as e:
                print(f"[ERROR] 병원 저장 실패: {item.get('INST_NM')} → {e}")
        session.commit()


def fetch_and_store_hospitals():
    items = fetch_hospitals()
    store_hospitals(items)
