from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from backend.app.api.security import create_access_token, get_current_user, hash_password, user_payload, verify_password
from backend.app.db.database import get_db
from backend.app.db.models import AuditEvent, UserAccount

router = APIRouter(tags=["Accounts"])


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)
    organization_name: str = Field(min_length=2, max_length=200)
    role: str = "business_owner"

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address.")
        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address.")
        return value


def _session(user: UserAccount) -> dict:
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_payload(user)}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    if db.query(UserAccount.id).filter(UserAccount.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    if not re.search(r"[A-Za-z]", payload.full_name):
        raise HTTPException(status_code=422, detail="Enter a valid name.")
    user = UserAccount(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        organization_name=payload.organization_name.strip(),
    )
    db.add(user)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="account.created", entity_type="account", entity_id=str(user.id), details={"role": user.role}))
    db.commit()
    db.refresh(user)
    return _session(user)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")
    db.add(AuditEvent(user_id=user.id, action="account.signed_in", entity_type="account", entity_id=str(user.id), details={}))
    db.commit()
    return _session(user)


@router.get("/me")
def current_account(user: UserAccount = Depends(get_current_user)):
    return {"user": user_payload(user)}
