# app/services/shelter_service.py
from app.db.session import db_engine
from app.models.shelter_models import Shelter
from sqlmodel import Session
import requests
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

def fetch_and_store_shelters():
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
        print("API call URL:", response.url)
        print("Status code:", response.status_code)
        print("First part of response text:", response.text[:300])
    except Exception as e:
        print("API request failed:", e)
        return

    try:
        data = response.json()
        print("JSON parsed successfully")
    except Exception as e:
        print("JSON parsing error:", e)
        return

    items = data.get("body", [])
    print("Number of shelters received:", len(items))

    if not items:
        print("No shelter data found.")
        return

    with Session(db_engine) as session:
        for item in items:
            try:
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
                print("Error adding shelter:", item.get("REARE_NM"), "->", e)
        session.commit()
        print("Shelter data insert completed")