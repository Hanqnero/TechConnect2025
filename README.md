# TechConnect2025

This repo contains a FastAPI backend and a React/Vite frontend.

## Prereqs
- Windows PowerShell
- Node.js 18+
- Python: managed via `uv` (installs local .venv automatically)

## Backend (FastAPI)
```powershell
# from repo root
uv venv .venv --clear
uv pip install -r app\requirements.txt -p .venv
$env:ALLOWED_ORIGINS = "http://localhost:5173"
.\.venv\Scripts\python.exe -m uvicorn app.app:app --reload --port 8000
```

Auth endpoints: POST /auth/register, POST /auth/login, POST /auth/logout, GET /auth/me

## Frontend (Vite)
```powershell
cd frontend
npm install
npm run dev
```

## Notes
- Credentials DB: `app/data/auth.db` (SQLite)
- App data DB: `app/database/sports.db`
- Cookie settings via env: COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_DOMAIN
- Vite dev proxy forwards /auth and /health to http://127.0.0.1:8000 so you can call relative paths in the frontend and keep cookies on the same origin.
