# Backend (FastAPI)

Run locally:

- Create & activate virtual env (optional)
- Install deps: `pip install -r app/requirements.txt`
- Start dev server: `uvicorn app.app:app --reload --port 8000`

Auth endpoints:
- POST /auth/register { login, password }
- POST /auth/login { login, password, remember }
- POST /auth/logout
- GET  /auth/me

Cookies:
- Session token set in `tc_session` (httpOnly). Configure via env vars:
  - ALLOWED_ORIGINS (comma list)
  - COOKIE_SECURE=true|false
  - COOKIE_SAMESITE=lax|strict|none
  - COOKIE_DOMAIN=your-domain
  - JWT_SECRET=change-me

Data stores:
- Credentials: `app/auth.db` (SQLite)
- App data: existing `app/data/sports.db`
