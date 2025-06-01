import pandas as pd
from sqlmodel import Session
from app.db.session import db_engine
from app.models.region_model import Region

def load_region_csv():
    df = pd.read_csv("data/RegionCategory.csv", encoding="utf-8")
    df = df.fillna("")
    regions = []
    for _, row in df.iterrows():
        sido = row["시도명"].strip()
        sigungu = row["시군구명"].strip()
        eupmyeondong = row["읍면동명"].strip()
        if sigungu == "":
            sigungu = None
        if eupmyeondong == "":
            eupmyeondong = None
        region = Region(
            sido=sido,
            sigungu=sigungu,
            eupmyeondong=eupmyeondong
        )
        regions.append(region)
    with Session(db_engine) as session:
        session.add_all(regions)
        session.commit()