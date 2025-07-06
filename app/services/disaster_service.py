import os
import requests
import pytz
import urllib3
from sqlmodel import Session, select
from datetime import datetime, timedelta
from dotenv import load_dotenv
from datetime import datetime, timedelta
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from app.services.disaster_region_service import parse_region_tuples, save_disaster_regions
from app.services.notification_service import enqueue_notifications

KST = pytz.timezone("Asia/Seoul")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"

def fetch_disaster_items():
    print(f"[INFO] DisasterInfo Fetch 시작 : {datetime.utcnow()}")
    today_str = datetime.utcnow().strftime('%Y%m%d')
    API_KEY = os.getenv("DISASTER_API_SERVICE_KEY")
    params = {
        "serviceKey": API_KEY,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "100",
        "crtDt": today_str
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()
    except Exception as e:
        print(f"[ERROR] DisasterInfo API 요청 실패: {e}")
        return []
    
    items = data.get("body")
    if not isinstance(items, list):
        print(f"[ERROR] Unexpected API format: body={items}")
        return []
    
    return items


def process_new_disasters(items, threshold):
    now = datetime.now(KST)
    with Session(db_engine) as session:
        for item in items:
            try:
                start_time = datetime.strptime(item.get("CRT_DT"), "%Y/%m/%d %H:%M:%S")
                start_time = KST.localize(start_time)
                if start_time < threshold:
                    continue
                
                region_str = item.get("RCPTN_RGN_NM", "")
                region_tuples = parse_region_tuples(region_str, session)
                if not region_tuples:
                    print("[SKIP] 파싱실패 - 유효 Region 없음")
                    continue
                
                # 중복 여부 확인
                existing = session.exec(
                    select(DisasterInfo).where(
                        DisasterInfo.start_time == start_time,
                        DisasterInfo.region_name == region_str
                    )
                ).first()
                if existing:
                    continue
                # 새로운 재난 정보 저장
                disaster = DisasterInfo(
                    disaster_type=item.get("DST_SE_NM", "기타"),
                    disaster_level=item.get("EMRG_STEP_NM", "알수없음"),
                    info=item.get("MSG_CN", ""),
                    active=True,
                    start_time=start_time,
                    updated_at=now,
                    region_name=region_str
                )
                session.add(disaster)
                session.flush()
                save_disaster_regions(session, disaster.id, region_tuples)
                enqueue_notifications(session, disaster)
            except Exception as e:
                print(f"[ERROR] Insert 실패: {e} (item: {item})")
                session.rollback()
                continue
        try:
            session.commit()
        except:
            print(f"[ERROR] Disasterinfo commit 실패: {e}")
            session.rollback()

def deactivate_old_disasters(threshold):
    with Session(db_engine) as session:
        try:
            old_disasters = session.exec(
                select(DisasterInfo).where(
                    DisasterInfo.start_time < threshold,
                    DisasterInfo.active == True
                )
            ).all()
            for old in old_disasters:
                old.active=False
            session.commit()
        except Exception as e:
            print(f"[ERROR] 비활성화 처리 실패: {e}")
            session.rollback()

def fetch_and_store_disasters():
    items = fetch_disaster_items()
    if not items:
        print("[INFO] 가져온 데이터 없음, 종료")
        return
    now = datetime.now(KST)
    threshold = now - timedelta(hours=3)
    
    process_new_disasters(items, threshold)
    deactivate_old_disasters(threshold)
