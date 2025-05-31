import os
import requests
from sqlmodel import Session
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from app.models.disaster_region_model import DisasterRegion
from datetime import datetime
from dotenv import load_dotenv
import urllib3
from sqlalchemy import or_

from app.models.region_model import Region

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"

def find_deepest_region(region_str, session):
    tokens = region_str.strip().split()
    # '부산광역시 전체' 등 '시도 전체'만 주어질 때 특별 처리
    if len(tokens) == 2 and tokens[1] == '전체':
        sido = tokens[0]
        region = session.query(Region).filter_by(sido=sido, sigungu=None, eupmyeondong=None).first()
        if region:
            return sido, None, None
    # 3단계(시도, 시군구, 읍면동) → 2단계(시도, 시군구) → 1단계(시도) 순으로 매칭
    if len(tokens) >= 3:
        sido, sigungu, eupmyeondong = tokens[0], tokens[1], tokens[2]
        region = session.query(Region).filter_by(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong
        ).first()
        if region:
            return sido, sigungu, eupmyeondong
    if len(tokens) >= 2:
        sido, sigungu = tokens[0], tokens[1]
        region = session.query(Region).filter_by(
            sido=sido, sigungu=sigungu
        ).first()
        if region:
            return sido, sigungu, None
    if len(tokens) >= 1:
        sido = tokens[0]
        region = session.query(Region).filter_by(
            sido=sido
        ).first()
        if region:
            return sido, None, None
    return None, None, None

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
                region_str = item.get("RCPTN_RGN_NM", "")
                region_name = region_str.strip()
                # 쉼표로 여러 지역이 구분되어 있을 때 각각 처리
                region_chunks = [chunk.strip() for chunk in region_str.split(',') if chunk.strip()]
                region_tuples = []
                for chunk in region_chunks:
                    sido, sigungu, eupmyeondong = find_deepest_region(chunk, session)
                    if sido:
                        region_tuples.append((sido, sigungu, eupmyeondong))
                        print(f"[파싱] sido={sido}, sigungu={sigungu}, eupmyeondong={eupmyeondong}")

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

                # region_tuples에서 중복 제거
                region_tuples = list(set(region_tuples))

                for sido, sigungu, eupmyeondong in region_tuples:
                    # eupmyeondong이 None/빈 문자열이면 NULL/빈 문자열도 매칭
                    if not eupmyeondong:
                        region = session.query(Region).filter(
                            Region.sido == sido,
                            Region.sigungu == sigungu,
                            or_(Region.eupmyeondong == None, Region.eupmyeondong == "")
                        ).first()
                    else:
                        region = session.query(Region).filter_by(
                            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong
                        ).first()
                    if region:
                        # DisasterRegion 중복 체크 후 insert
                        exists = session.query(DisasterRegion).filter_by(
                            disaster_id=disaster.id, region_id=region.id
                        ).first()
                        if not exists:
                            disaster_region = DisasterRegion(disaster_id=disaster.id, region_id=region.id)
                            session.add(disaster_region)
                    else:
                        print(f"[!] Region 매칭 실패: sido={sido}, sigungu={sigungu}, eupmyeondong={eupmyeondong}")
            except Exception as e:
                print("Error saving disaster:", e)
        try:
            session.commit()
        except Exception as e:
            print(f"[!] DB 저장 실패: {e}")
            session.rollback()

