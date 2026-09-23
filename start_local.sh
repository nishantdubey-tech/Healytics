#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 -m venv backend/.venv 2>/dev/null || true
. backend/.venv/bin/activate
pip install -r backend/requirements.txt
( cd backend && uvicorn app.main:app --reload --port 8000 ) &
cd frontend
npm install
npm run dev
