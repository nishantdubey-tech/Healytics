from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .api.routes import router
from .services.ml import ensure_model

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healytics",
    description="AI/ML platform for clinical data insights and academic risk prediction",
    version="1.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    ensure_model()

app.include_router(router, prefix="/api", tags=["Healytics"])

frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.get("/")
def root():
    return {"message": "Healytics API is online", "docs": "/docs"}
