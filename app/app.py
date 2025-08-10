from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .auth.router import router as auth_router
from .config import settings
from .sports_router import router as sports_router


app = FastAPI(title=settings.title, version=settings.version)

# CORS for local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# Mount routers
app.include_router(auth_router)
app.include_router(sports_router)

# Uvicorn entrypoint hint: `uvicorn app.app:app --reload`
