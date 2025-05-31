from app.models.disaster_region_model import DisasterRegion
from app.models.region_model import Region
from sqlalchemy import or_

def parse_region_tuples(region_str, session):
    region_chunks = [chunk.strip() for chunk in region_str.split(',') if chunk.strip()]
    region_tuples = []
    for chunk in region_chunks:
        sido, sigungu, eupmyeondong = find_deepest_region(chunk, session)
        if sido:
            region_tuples.append((sido, sigungu, eupmyeondong))
            print(f"[파싱] sido={sido}, sigungu={sigungu}, eupmyeondong={eupmyeondong}")
    return list(set(region_tuples))

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

def save_disaster_regions(session, disaster_id, region_tuples):
    for sido, sigungu, eupmyeondong in region_tuples:
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
            exists = session.query(DisasterRegion).filter_by(
                disaster_id=disaster_id, region_id=region.id
            ).first()
            if not exists:
                disaster_region = DisasterRegion(disaster_id=disaster_id, region_id=region.id)
                session.add(disaster_region)
        else:
            print(f"[!] Region 매칭 실패: sido={sido}, sigungu={sigungu}, eupmyeondong={eupmyeondong}") 