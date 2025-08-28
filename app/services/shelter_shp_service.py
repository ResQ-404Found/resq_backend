# app/services/shelter_shp_service.py
import os
import math
import geopandas as gpd
from typing import Optional
from sqlmodel import Session, select
from app.db.session import db_engine
from app.models.shelter_models import Shelter

# 환경변수 (없으면 기본값)
SHP_PATH = os.getenv("SHELTER_SHP_PATH", "./data/민방위대피소.shp")
SHP_SOURCE_EPSG = int(os.getenv("SHELTER_SHP_EPSG", "5179"))  # 보통 5179
TARGET_EPSG = 4326  # DB/서비스는 WGS84 위경도

def _pick(cols: dict, *keys):
    """여러 후보 컬럼명 중 먼저 존재하는 값을 반환"""
    for k in keys:
        if k in cols and cols[k] is not None and str(cols[k]).strip() != "":
            return cols[k]
    return None

def _to_float_safe(v) -> Optional[float]:
    try:
        f = float(v)
        if math.isfinite(f):
            return f
    except:
        pass
    return None

def load_shelters_from_shp(shp_path: Optional[str] = None) -> int:
    """
    SHP 읽어서 Shelter DB에 넣기(중복 관리번호 건너뜀).
    반환: 신규 insert 개수
    """
    path = shp_path or SHP_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"SHP 파일이 없음: {path}")

    # 1) 읽기 + 좌표계 세팅/변환
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        # SHP에 CRS가 비면 환경변수 기반으로 가정
        gdf.set_crs(epsg=SHP_SOURCE_EPSG, inplace=True)
    if gdf.crs.to_epsg() != TARGET_EPSG:
        gdf = gdf.to_crs(epsg=TARGET_EPSG)

    inserted = 0
    with Session(db_engine) as session:
        for _, row in gdf.iterrows():
            # 지오메트리에서 lon/lat 추출
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue
            lon = _to_float_safe(getattr(geom, "x", None))
            lat = _to_float_safe(getattr(geom, "y", None))
            if lat is None or lon is None:
                continue

            # 컬럼 매핑 (데이터셋마다 컬럼명이 다를 수 있어 후보 지정)
            cols = dict(row)

            mng_sn = _pick(cols, "MNG_SN", "관리번호", "mng_sn", "관리_번호")
            name = _pick(cols, "REARE_NM", "시설명", "name")
            addr = _pick(cols, "RONA_DADDR", "주소", "road_address")
            type_code = _pick(cols, "SHLT_SE_CD", "유형코드", "type_code")
            type_name = _pick(cols, "SHLT_SE_NM", "유형명", "type_name")

            # 관리번호 없으면 좌표중복/이름중복 등 다른 기준으로 처리할 수 있지만,
            # 일단 관리번호 없는 레코드는 skip
            if not mng_sn:
                continue

            # 이미 있으면 skip (upsert 필요하면 여기서 update 처리)
            exists = session.exec(
                select(Shelter).where(Shelter.management_serial_number == str(mng_sn))
            ).first()
            if exists:
                # 예: 주소/좌표 보정 업데이트를 원하면 아래 주석 해제
                # exists.facility_name = name or exists.facility_name
                # exists.road_address = addr or exists.road_address
                # exists.latitude = lat if lat is not None else exists.latitude
                # exists.longitude = lon if lon is not None else exists.longitude
                # exists.shelter_type_code = int(type_code) if type_code is not None else exists.shelter_type_code
                # exists.shelter_type_name = type_name or exists.shelter_type_name
                # session.add(exists)
                continue

            shelter = Shelter(
                facility_name = str(name) if name else "이름없음",
                road_address = str(addr) if addr else None,
                latitude = lat,
                longitude = lon,
                shelter_type_code = int(type_code) if type_code is not None else None,
                shelter_type_name = str(type_name) if type_name else None,
                management_serial_number = str(mng_sn),
            )
            session.add(shelter)
            inserted += 1

        session.commit()

    return inserted
