import os
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Request

from .db import get_user_by_id

_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")

def _sign(data: bytes) -> str:
    import base64
    sig = hmac.new(_SECRET.encode("utf-8"), data, digestmod="sha256").digest()
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")

def _b64e(b: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")

def _b64d(s: str) -> bytes:
    import base64
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def create_access_token(payload: Dict[str, Any], expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    header = {"alg": "HS256", "typ": "JWT"}
    body = {**payload, "exp": int(exp.timestamp())}
    h = _b64e(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    b = _b64e(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    s = _sign(f"{h}.{b}".encode("ascii"))
    return f"{h}.{b}.{s}"

def _decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        h_b64, b_b64, sig = token.split(".")
        expected_sig = _sign(f"{h_b64}.{b_b64}".encode("ascii"))
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(_b64d(b_b64))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except Exception:
        return None

async def get_current_user_optional(request: Request):
    token = request.cookies.get("tc_session")
    if not token:
        return None
    payload = _decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
    except Exception:
        return None
    return get_user_by_id(user_id_int)
