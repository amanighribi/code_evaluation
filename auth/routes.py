from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth.db import create_user, get_user_by_username, init_users_db
from auth.security import hash_password, verify_password, create_access_token

init_users_db()

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest):
    if len(data.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    password_hash = hash_password(data.password)
    created = create_user(data.username.strip(), password_hash)

    if not created:
        raise HTTPException(status_code=409, detail="Username already taken.")

    token = create_access_token(data.username.strip())
    return TokenResponse(access_token=token, username=data.username.strip())


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = get_user_by_username(data.username.strip())
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    token = create_access_token(user["username"])
    return TokenResponse(access_token=token, username=user["username"])