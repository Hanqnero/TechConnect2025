import os
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import json

from fastapi import Depends, HTTPException, status, Request

from .auth_db import get_user_by_id
from .passwords import verify_password


# Minimal JWT-like token using HMAC-SHA256 (no external deps)
_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")


def _sign(data: bytes) -> str:
    sig = hmac.new(_SECRET.encode("utf-8"), data, hashlib.sha256).digest()
    return _b64e(sig)


def create_access_token(payload: Dict[str, Any], expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    """Deprecated: auth moved to app.auth.*

    Use app.auth.security for token helpers and app.auth.db for DB access.
    """

    from .auth.security import *  # re-export for compatibility
    h = _b64e(json.dumps(header, separators=(",", ":")).encode("utf-8"))
