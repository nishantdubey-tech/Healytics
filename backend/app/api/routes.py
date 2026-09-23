import io
import os
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from passlib.context import CryptContext
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PatientRecord
from ..schemas import LoginRequest, LoginResponse, PatientDataInput, PatientRecordResponse, PredictionResponse
from ..services.ml import analyze_csv, predict_heart

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")

def make_token(username: str):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=12)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@router.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    expected_user = os.getenv("DEMO_USERNAME", "demo")
    expected_password = os.getenv("DEMO_PASSWORD", "healytics123")
    if not secrets.compare_digest(body.username, expected_user) or not secrets.compare_digest(body.password, expected_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": make_token(body.username), "username": body.username}

@router.get("/health")
def health():
    return {"status": "healthy", "service": "healytics"}

@router.post("/predict", response_model=PredictionResponse)
def predict(body: PatientDataInput, db: Session = Depends(get_db)):
    data = body.model_dump()
    prediction, probability, risk, explanation = predict_heart(data)

    record = PatientRecord(
        **data,
        prediction_result=prediction,
        probability_score=probability,
        risk_level=risk
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "prediction": prediction,
        "probability": probability,
        "risk_level": risk,
        "explanation": explanation,
        "timestamp": record.timestamp
    }

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), target_column: Optional[str] = None):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV file is too large. Maximum is 10 MB.")
    try:
        return analyze_csv(content, target_column)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/history", response_model=List[PatientRecordResponse])
def history(db: Session = Depends(get_db)):
    return db.query(PatientRecord).order_by(PatientRecord.timestamp.desc()).limit(100).all()

@router.get("/analytics/summary")
def summary(db: Session = Depends(get_db)):
    records = db.query(PatientRecord).all()
    total = len(records)
    high = sum(1 for r in records if r.prediction_result == 1)
    avg = sum(r.probability_score for r in records) / total if total else 0
    return {
        "total_analyzed": total,
        "high_risk_cases": high,
        "low_risk_cases": total - high,
        "average_risk_probability": round(avg, 4)
    }

@router.get("/model/metrics")
def model_metrics():
    import json
    from ..services.ml import METRICS_PATH, train_heart_model
    if not METRICS_PATH.exists():
        train_heart_model()
    return json.loads(METRICS_PATH.read_text())

@router.post("/report")
def report(body: dict):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Healytics - Clinical Risk Analysis")
    y -= 35
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Academic/demo decision-support report. Not a diagnosis.")
    y -= 30

    for key, value in body.items():
        if key == "explanation" and isinstance(value, list):
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Top explanatory factors")
            y -= 18
            c.setFont("Helvetica", 10)
            for item in value[:8]:
                c.drawString(65, y, f"{item.get('feature')}: {item.get('impact')}")
                y -= 16
        else:
            text = f"{key}: {value}"
            c.drawString(50, y, text[:110])
            y -= 16
        if y < 60:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=healytics-report.pdf"}
    )
