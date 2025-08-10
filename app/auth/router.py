from fastapi import APIRouter, Depends, HTTPException, status, Response
from datetime import timedelta
import os

from .models import RegisterRequest, LoginRequest, UserPublic
from .db import init_auth_db, get_user_by_login, create_user, update_last_login
from .security import create_access_token, get_current_user_optional
from ..passwords import verify_password
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.on_event("startup")
def on_startup():
    init_auth_db()
    # Seed a test teacher user for development convenience
    try:
        if not get_user_by_login("tina"):
            create_user("tina", "password123")
    except Exception:
        # Non-fatal if seeding fails (e.g., concurrent startup)
        pass

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest) -> UserPublic:
    existing = get_user_by_login(req.login)
    if existing:
        raise HTTPException(status_code=409, detail="Логин уже занят")
    user = create_user(req.login, req.password)
    return UserPublic(**user)

@router.post("/login")
def login(req: LoginRequest, response: Response) -> dict:
    user = get_user_by_login(req.login)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    expires = timedelta(days=30) if req.remember else timedelta(hours=12)
    token = create_access_token({"sub": str(user["id"]), "login": user["login"]}, expires_delta=expires)

    cookie_secure = settings.cookie_secure
    cookie_samesite = settings.cookie_samesite
    cookie_domain = settings.cookie_domain
    response.set_cookie(
        key="tc_session",
        value=token,
        max_age=int(expires.total_seconds()),
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        domain=cookie_domain,
        path="/",
    )

    update_last_login(user["id"])  # non-critical

    return {"message": "вход выполнен", "user": {"id": user["id"], "login": user["login"]}}

@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie("tc_session", path="/")
    return {"message": "выход выполнен"}

@router.get("/me")
def me(user = Depends(get_current_user_optional)):
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": {"id": user["id"], "login": user["login"], "created_at": user["created_at"], "last_login_at": user["last_login_at"]}}
