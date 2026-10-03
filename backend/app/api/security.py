"""Lightweight signed sessions and password hashing for the small API service."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import UserAccount

_bearer = HTTPBearer(auto_error=False)
_runtime_secret = secrets.token_bytes(32)
SESSION_SECONDS = 60 * 60 * 12
PASSWORD_ROUNDS = 310_000


def _secret() -> bytes:
    configured = os.getenv("AUTH_SECRET_KEY", "").strip()
    return configured.encode("utf-8") if configured else _runtime_secret


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ROUNDS)
    return f"pbkdf2_sha256${PASSWORD_ROUNDS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(derived).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds_text, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds_text))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user: UserAccount) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": int(time.time()) + SESSION_SECONDS,
        "nonce": secrets.token_urlsafe(8),
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=")
    signature = hmac.new(_secret(), encoded, hashlib.sha256).digest()
    return encoded.decode() + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode()


def _decode_token(token: str) -> dict:
    try:
        encoded, signature_text = token.split(".", 1)
        supplied = base64.urlsafe_b64decode(signature_text + "=" * (-len(signature_text) % 4))
        expected = hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(supplied, expected):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("expired")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Sign in again.")


def user_payload(user: UserAccount) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "organization_name": user.organization_name,
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> UserAccount:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.")
    payload = _decode_token(credentials.credentials)
    user = db.query(UserAccount).filter(UserAccount.id == payload.get("sub")).first()
    if user is None or not user.is_active or user.role != payload.get("role"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This account is unavailable. Sign in again.")
    return user


def require_roles(*roles: str) -> Callable:
    def dependency(user: UserAccount = Depends(get_current_user)) -> UserAccount:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account does not have access to this action.")
        return user
    return dependency
