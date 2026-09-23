from datetime import datetime
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class PatientDataInput(BaseModel):
    patient_name: str = "Demo Patient"
    age: int = Field(..., ge=1, le=120)
    sex: int = Field(..., ge=0, le=1)
    cp: int = Field(..., ge=0, le=3)
    trestbps: int = Field(..., ge=50, le=260)
    chol: int = Field(..., ge=50, le=700)
    fbs: int = Field(..., ge=0, le=1)
    restecg: int = Field(..., ge=0, le=2)
    thalach: int = Field(..., ge=40, le=250)
    exang: int = Field(..., ge=0, le=1)
    oldpeak: float = Field(..., ge=0, le=10)
    slope: int = Field(..., ge=0, le=3)
    ca: int = Field(..., ge=0, le=4)
    thal: int = Field(..., ge=0, le=7)

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    explanation: list[dict]
    timestamp: datetime

class PatientRecordResponse(BaseModel):
    id: int
    patient_name: str
    age: int
    prediction_result: int
    probability_score: float
    risk_level: str
    timestamp: datetime

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
