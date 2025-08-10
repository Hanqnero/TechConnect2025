import os
from typing import List

class Settings:
    title: str = os.getenv("APP_TITLE", "TechConnect API")
    version: str = os.getenv("APP_VERSION", "0.1.0")

    # CORS
    def allowed_origins(self) -> List[str]:
        origins = os.getenv("ALLOWED_ORIGINS")
        if origins:
            return [o.strip() for o in origins.split(",") if o.strip()]
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    # Cookies
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    cookie_samesite: str = os.getenv("COOKIE_SAMESITE", "lax")
    cookie_domain: str | None = os.getenv("COOKIE_DOMAIN")

settings = Settings()
