from langchain.schema import Document
from sqlmodel import Session, select
from app.db.session import db_engine
from app.models.disaster_model import DisasterInfo
from app.models.hospital_model import Hospital, HospitalOperatingHour
from app.models.shelter_models import Shelter


def load_shelters_as_docs(limit: int = 20):
    with Session(db_engine) as session:
        shelters = session.exec(select(Shelter).limit(limit)).all()
        return [
            Document(
                page_content=f"{s.facility_name}, {s.road_address}, 유형: {s.shelter_type_name}",
                metadata={
                    "id": s.id,
                    "category": "shelter", 
                    "shelter_type_code": s.shelter_type_code,
                    "management_serial_number": s.management_serial_number
                }
            )
            for s in shelters
        ]


def load_hospitals_with_hours_as_docs(limit: int = 20):
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
                        "category": "hospital",
                        "latitude": h.latitude,
                        "longitude": h.longitude,
                        "phone_number": h.phone_number,
                        "emergency_room": h.emergency_room,
                        "weekend_operating": h.weekend_operating
                    }
                )
            )
        return docs


def load_disasters_as_docs(limit: int = 20):
    with Session(db_engine) as session:
        disasters = session.exec(
            select(DisasterInfo).where(DisasterInfo.active == True).limit(limit)
        ).all()
        return [
            Document(
                page_content=f"[{d.disaster_type} - {d.disaster_level}] {d.info}",
                metadata={
                    "id": str(d.id),
                    "category": "disaster",
                    "type": d.disaster_type,
                    "level": d.disaster_level,
                    "region": d.region_name,
                    "start_time": str(d.start_time) if d.start_time else None,
                    "end_time": str(d.end_time) if d.end_time else None,
                    "updated_at": str(d.updated_at) if d.updated_at else None,
                    "active": bool(d.active)
                }
            )
            for d in disasters
        ]
