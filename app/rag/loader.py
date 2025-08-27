from langchain.schema import Document
from sqlmodel import Session, select
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from app.models.hospital_model import Hospital, HospitalOperatingHour
from app.models.shelter_models import Shelter


# 🏠 Shelter (10개만 불러오기)
def load_shelters_as_docs(limit: int = 10):
    with Session(db_engine) as session:
        shelters = session.exec(select(Shelter).limit(limit)).all()
        return [
            Document(
                page_content=f"{s.facility_name}, {s.road_address}, 유형: {s.shelter_type_name}",
                metadata={
                    "id": s.id,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "shelter_type_code": s.shelter_type_code,
                    "management_serial_number": s.management_serial_number
                }
            )
            for s in shelters
        ]


# 🏥 Hospital + HospitalOperatingHour (10개만 불러오기)
def load_hospitals_with_hours_as_docs(limit: int = 10):
    with Session(db_engine) as session:
        hospitals = session.exec(select(Hospital).limit(limit)).all()
        docs = []

        for h in hospitals:
            hours = session.exec(
                select(HospitalOperatingHour).where(HospitalOperatingHour.hospital_id == h.id)
            ).all()

            if hours:
                hours_text = "\n".join([
                    f"{ho.day_of_week}: {ho.open_time} ~ {ho.close_time} ({'휴무' if ho.is_closed else '운영'})"
                    for ho in hours
                ])
            else:
                hours_text = "운영 시간 정보 없음"

            docs.append(
                Document(
                    page_content=(
                        f"{h.facility_name}, {h.road_address}, 전화: {h.phone_number}, "
                        f"응급실: {h.emergency_room}, 주말진료: {h.weekend_operating}\n"
                        f"운영시간:\n{hours_text}"
                    ),
                    metadata={
                        "id": h.id,
                        "latitude": h.latitude,
                        "longitude": h.longitude,
                        "phone_number": h.phone_number,
                        "emergency_room": h.emergency_room,
                        "weekend_operating": h.weekend_operating
                    }
                )
            )
        return docs


# 🚨 DisasterInfo (10개만 불러오기, active=True만)
def load_disasters_as_docs(limit: int = 10):
    with Session(db_engine) as session:
        disasters = session.exec(
            select(DisasterInfo).where(DisasterInfo.active == True).limit(limit)
        ).all()
        return [
            Document(
                page_content=f"[{d.disaster_type} - {d.disaster_level}] {d.info}",
                metadata={
                    "id": d.id,
                    "type": d.disaster_type,
                    "level": d.disaster_level,
                    "region": d.region_name,
                    "start_time": d.start_time,
                    "end_time": d.end_time,
                    "updated_at": d.updated_at,
                    "active": d.active
                }
            )
            for d in disasters
        ]
