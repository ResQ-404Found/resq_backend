import pandas as pd
from app.models.ai_model import model, label_encoder

def predict_damage(date: str, region: str, avgTa: float, sumRn: float, avgWs: float, message_exists: bool, lat=None, lon=None):
    # 지역 검증
    if region not in label_encoder.classes_:
        raise ValueError(f"'{region}' 지역은 학습 데이터에 없음.")

    region_encoded = label_encoder.transform([region])[0]

    # feature 구성
    X_new = pd.DataFrame([{
        "avgTa": avgTa,
        "sumRn": sumRn,
        "avgWs": avgWs,
        "disaster_flag": int(message_exists),
        "region_encoded": region_encoded
    }])

    pred = model.predict(X_new)[0]

    return {
        "date": date,
        "region": region,
        "pred_damage": round(float(pred), 5),  # ha 단위
        "lat": lat,
        "lon": lon
    }
