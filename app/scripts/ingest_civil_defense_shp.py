# app/scripts/ingest_civil_defense_shp.py
import argparse
import math
from typing import Optional

import geopandas as gpd
import pandas as pd
from sqlmodel import Session, select

from app.db.session import db_engine
from app.models.shelter_models import Shelter

# ─────────────────────────────────────────────────────────────────
# 필드 매핑(필요하면 여기만 바꾸면 됨)
NAME_CANDIDATES     = ["MGC_NM", "name", "REARE_NM", "FAC_NAME", "시설명"]
ADDRESS_CANDIDATES  = ["RONA_DADDR", "ADDRESS", "addr", "도로명주소", "주소"]
TYPE_NAME_DEFAULT   = "민방위대피소"
TYPE_CODE_DEFAULT   = 9001  # 프로젝트 규칙에 맞게 원하는 코드 숫자 사용
EXTERNAL_ID_FIELDS  = ["MNG_SN", "관리번호", "관리ID"]
# ─────────────────────────────────────────────────────────────────

def _pick_first(d: dict, keys: list[str]) -> Optional[str]:
    for k in keys:
        if k in d and pd.notna(d[k]) and str(d[k]).strip():
            return str(d[k]).strip()
    return None

def _safe_float(x) -> Optional[float]:
    try:
        v = float(x)
        if math.isfinite(v):
            return v
    except Exception:
        pass
    return None

def _get_lat_lon(row) -> tuple[Optional[float], Optional[float]]:
    # 1) LA/LO 우선
    la = _safe_float(row.get("LA"))
    lo = _safe_float(row.get("LO"))
    if la is not None and lo is not None:
        return la, lo

    # 2) geometry 포인트에서 추출
    geom = row.get("geometry")
    if geom is not None and hasattr(geom, "x") and hasattr(geom, "y"):
        return _safe_float(geom.y), _safe_float(geom.x)

    return None, None

def _find_existing(session: Session, name: str, lat: float, lon: float, external_id: Optional[str]):
    # external_id가 있으면 그걸로 1차 조회
    if external_id:
        q = select(Shelter).where(Shelter.management_serial_number == external_id)
        found = session.exec(q).first()
        if found:
            return found

    # 이름 + 좌표 근접(라운드)로 fallback
    lat_r = round(lat, 6); lon_r = round(lon, 6)
    q = select(Shelter).where(
        (Shelter.facility_name == name) &
        (Shelter.latitude  >= lat_r - 1e-5) & (Shelter.latitude  <= lat_r + 1e-5) &
        (Shelter.longitude >= lon_r - 1e-5) & (Shelter.longitude <= lon_r + 1e-5)
    )
    return session.exec(q).first()

def ingest(shp_path: str, source_label: str = "민방위"):
    gdf = gpd.read_file(shp_path)

    # 좌표계 확실히 지정(대부분 EPSG:4326; 아니라면 여기서 to_crs 해주세요)
    if gdf.crs is None:
        # 필요시 gdf.set_crs("EPSG:4326", inplace=True)
        pass
    elif gdf.crs.to_epsg() not in (4326, None):
        gdf = gdf.to_crs(4326)

    added, updated, skipped = 0, 0, 0

    with Session(db_engine) as session:
        for _, row in gdf.iterrows():
            row_dict = row if isinstance(row, dict) else row.to_dict()

            name     = _pick_first(row_dict, NAME_CANDIDATES) or "무명 대피소"
            address  = _pick_first(row_dict, ADDRESS_CANDIDATES)
            ext_id   = _pick_first(row_dict, EXTERNAL_ID_FIELDS)
            lat, lon = _get_lat_lon(row_dict)
            if lat is None or lon is None:
                skipped += 1
                continue

            # 타입 이름/코드
            type_name = TYPE_NAME_DEFAULT
            type_code = TYPE_CODE_DEFAULT

            # 기존 레코드 있는지 확인
            ex = _find_existing(session, name, lat, lon, ext_id)

            if ex:
                # 필요한 필드만 보수적으로 업데이트
                changed = False

                if address and ex.road_address != address:
                    ex.road_address = address; changed = True
                if ex.shelter_type_name != type_name:
                    ex.shelter_type_name = type_name; changed = True
                if ex.shelter_type_code != type_code:
                    ex.shelter_type_code = type_code; changed = True
                if getattr(ex, "source", None) != source_label:
                    try:
                        ex.source = source_label; changed = True
                    except Exception:
                        pass
                if ext_id and ex.management_serial_number != ext_id:
                    ex.management_serial_number = ext_id; changed = True

                if changed:
                    session.add(ex)
                    updated += 1
                else:
                    skipped += 1
            else:
                # 새로 추가
                s = Shelter(
                    facility_name=name,
                    road_address=address,
                    latitude=lat,
                    longitude=lon,
                    shelter_type_code=type_code,
                    shelter_type_name=type_name,
                    management_serial_number=ext_id,
                )
                # (선택) 모델에 source 컬럼이 있다면 저장
                try:
                    setattr(s, "source", source_label)
                except Exception:
                    pass

                session.add(s)
                added += 1

        session.commit()

    print(f"[DONE] added={added}, updated={updated}, skipped={skipped}")

def main():
    ap = argparse.ArgumentParser(description="Ingest Civil Defense SHP into DB")
    ap.add_argument("--shp", required=True, help="Path to 민방위대피소.shp")
    ap.add_argument("--source", default="민방위", help="source label to store")
    args = ap.parse_args()

    ingest(args.shp, args.source)

if __name__ == "__main__":
    main()
