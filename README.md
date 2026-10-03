# Healytics — AI/ML Driven Platform for Clinical Data Insights & Risk Prediction

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live--Demo-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://healytics-eight.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Healytics** is an academic clinical decision-support demo for exploring risk predictions on patient records and tabular datasets. It is not a medical device and must not be used for clinical diagnosis.

## Academic Project

- Institution: Jaypee Institute of Information Technology (JIIT), Noida
- Department: Electronics & Communication Engineering
- Project: Healytics — AI-ML Driven Platform for Clinical Data Insights and Risk Prediction
- Academic session: 2025–2026
- Supervisor: Dr. Radha Raman Pandey, Assistant Professor Senior Grade
- Team: Nishant Dubey (database management and testing), Nikhil Pandey (backend and AI logic), Akarsh Jain (frontend and UI design)

## Live Demo

- Web application: https://healytics-eight.vercel.app
- API health check: https://healytics-eight.vercel.app/api/health
- Demo access is configured with DEMO_USERNAME and DEMO_PASSWORD environment variables. Do not use source-code defaults on a public deployment.

## Features

1. Heart-disease risk prediction using a Random Forest model trained on the UCI Cleveland Heart Disease dataset.
2. Feature-impact explanations for factors including age, cholesterol, maximum heart rate, resting blood pressure, and angina.
3. CSV analysis that detects numeric and categorical fields and selects a classification or regression strategy.
4. Dashboard charts for risk distribution and aggregate analysis statistics.
5. PDF summaries with patient metrics and explanatory factors.
6. Vercel serverless adapters with temporary SQLite and model-storage fallbacks.

## Architecture

    React + Vite UI → FastAPI API → ML engine and SQLite/PostgreSQL

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, Lucide Icons, Axios, CSS |
| Backend | Python 3.9+, FastAPI, Uvicorn, Pydantic, PyJWT, Passlib |
| Machine learning | Scikit-learn, Pandas, NumPy, Joblib, SHAP |
| Persistence and reports | SQLAlchemy, SQLite/PostgreSQL, ReportLab |
| Deployment | Vercel serverless functions, Docker |

## Local Setup

Prerequisites: Python 3.9+, Node.js 18+, and npm.

    git clone https://github.com/nishantdubey-tech/Healytics.git
    cd Healytics
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Configure DEMO_USERNAME, DEMO_PASSWORD, and JWT_SECRET in your environment before starting the backend. Keep the values private and use unique, strong values for every deployment.

    python3 -m uvicorn app.main:app --reload --port 8000

The API runs at http://localhost:8000 (docs: http://localhost:8000/docs). In a second terminal:

    cd frontend
    npm install
    npm run dev

The frontend runs at http://localhost:5173.

## Vercel Deployment

Repository configuration files: [api/index.py](api/index.py), [vercel.json](vercel.json), and [requirements.txt](requirements.txt). Set DEMO_USERNAME, DEMO_PASSWORD, and JWT_SECRET in Vercel project environment settings before deployment; do not commit these values.

    npm install -g vercel
    vercel login
    vercel --prod

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/health | Service health |
| POST | /api/auth/login | Authentication and JWT generation |
| POST | /api/predict | Risk prediction for a patient record |
| POST | /api/upload | Analyze an uploaded CSV file |
| GET | /api/history | Retrieve recent prediction history |
| GET | /api/analytics/summary | Aggregate risk statistics |
| POST | /api/report | Generate a PDF summary |

## Disclaimer

This application was developed for academic, research, and decision-support demonstration purposes at JIIT Noida. It is not a certified medical device. Its predictions must not be used as clinical diagnoses.

## License

MIT License — see [LICENSE](LICENSE).
