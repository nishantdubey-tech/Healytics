# Healytics — AI/ML Driven Platform for Clinical Data Insights & Risk Prediction

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live--Demo-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://healytics-antigravity.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Healytics** is an end-to-end clinical decision-support web application that transforms raw medical records and tabular patient datasets into actionable risk predictions and explainable AI insights.

---

## 🏫 Academic Project Details

* **Institution:** Jaypee Institute of Information Technology (JIIT), Noida
* **Department:** Department of Electronics & Communication Engineering (ECE)
* **Project Title:** *Healytics: An AI-ML Driven Platform for Clinical Data Insights and Risk Prediction*
* **Academic Session:** 2025 – 2026
* **Supervisor:** Dr. Radha Raman Pandey *(Assistant Professor Senior Grade)*

### 👨‍💻 Project Team
* **Nishant Dubey** (Enrolment No: 23102066) — *Database Management & Testing*
* **Nikhil Pandey** (Enrolment No: 23802002) — *Backend Development & AI Logic*
* **Akarsh Jain** (Enrolment No: 23102004) — *Frontend Development & UI Design*

---

## 🌐 Live Demo & Deployment

* **Live Web Application (Vercel):** [https://healytics-antigravity.vercel.app](https://healytics-antigravity.vercel.app)
* **Backend API Health Check:** `https://healytics-antigravity.vercel.app/api/health`
* **Default Demo Credentials:**
  * **Username:** `demo`
  * **Password:** `healytics123`

---

## ✨ Key Features

1. **Patient Risk Prediction**: Real-time heart disease risk classification (Low, Moderate, High Risk) powered by Random Forest trained on the UCI Cleveland Heart Disease dataset.
2. **Explainable AI (SHAP / Feature Impact)**: Transparent decision-making breaking down exact risk factors (Age, Cholesterol, Max Heart Rate, Resting BP, Angina) for doctors.
3. **Automated Data Cleaning & Strategy Engine**: Upload any custom CSV dataset; the system automatically detects numeric/categorical fields and selects between Classification (Random Forest) and Regression (Gradient Boosting).
4. **Interactive Analytics Dashboard**: Visual charts depicting patient risk distribution, total cases analyzed, and real-time risk statistics.
5. **PDF Report Generation**: Downloadable medical risk report with patient metrics and top explanatory risk factors.
6. **Vercel Serverless Ready**: Production-tuned for serverless deployment with fallback `/tmp` SQLite and model storage handlers.

---

## 🏗 System Architecture

```
                               ┌─────────────────────────┐
                               │     React + Vite UI     │
                               │   (Presentation Tier)   │
                               └────────────┬────────────┘
                                            │ HTTP / JSON API
                               ┌────────────▼────────────┐
                               │   FastAPI Web Server    │
                               │   (Business Logic)      │
                               └────────────┬────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
       ┌────────────▼────────────┐                     ┌────────────▼────────────┐
       │   Random Forest / GB    │                     │    SQLite / Postgres    │
       │    ML Engine + SHAP     │                     │     Database Store      │
       └─────────────────────────┘                     └─────────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | React 18, Vite, Lucide Icons, Axios, CSS3 |
| **Backend** | Python 3.9+, FastAPI, Uvicorn, Pydantic, PyJWT, Passlib |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib, SHAP |
| **Database & Persistence** | SQLite / PostgreSQL, SQLAlchemy ORM |
| **PDF Generation** | ReportLab |
| **Cloud Deployment** | Vercel (Serverless Functions), Docker |

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.9+** installed
* **Node.js (v18+)** and **npm** installed

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/healytics.git
cd healytics
```

### 2. Backend Setup & Local Server

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional)
python3 -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend server
python3 -m uvicorn app.main:app --reload --port 8000
```
API endpoints will be available at `http://localhost:8000` (Swagger docs: `http://localhost:8000/docs`).

### 3. Frontend Setup & Run

In a second terminal window:

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## ☁️ Deploying to Vercel

The project includes pre-configured Vercel serverless adapters:
* [`api/index.py`](file:///Users/nishantdubey/Downloads/Healytics_Antigravity/api/index.py) — Serverless Function Entrypoint
* [`vercel.json`](file:///Users/nishantdubey/Downloads/Healytics_Antigravity/vercel.json) — Routing and Static Output Config
* [`requirements.txt`](file:///Users/nishantdubey/Downloads/Healytics_Antigravity/requirements.txt) — Optimized Serverless Dependencies

To deploy directly via Vercel CLI:

```bash
npm install -g vercel
vercel login
vercel --prod
```

---

## 📌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status |
| `POST` | `/api/auth/login` | User authentication & JWT generation |
| `POST` | `/api/predict` | Run heart risk ML model on patient record |
| `POST` | `/api/upload` | Upload & auto-analyze custom CSV datasets |
| `GET` | `/api/history` | Retrieve prediction history |
| `GET` | `/api/analytics/summary` | Dashboard metrics & aggregate risk stats |
| `POST` | `/api/report` | Generate downloadable PDF summary report |

---

## ⚠️ Disclaimer

> **Medical Disclaimer:** This application is developed strictly for academic, research, and decision-support demonstration purposes as part of the B.Tech curriculum at JIIT Noida. It is **not** a certified medical device. Predictions generated by this system must not be used as clinical diagnoses.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
