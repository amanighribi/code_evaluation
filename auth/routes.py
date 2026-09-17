from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth.db import create_user, get_user_by_username, init_users_db, VALID_ROLES
from auth.security import hash_password, verify_password, create_access_token

init_users_db()

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "student"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest):
    username = data.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role must be 'student' or 'teacher'.")

    created = create_user(username, hash_password(data.password), data.role)
    if not created:
        raise HTTPException(status_code=409, detail="Username already taken.")

    token = create_access_token(username, data.role)
    return TokenResponse(access_token=token, username=username, role=data.role)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = get_user_by_username(data.username.strip())
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    token = create_access_token(user["username"], user["role"])
    return TokenResponse(access_token=token, username=user["username"], role=user["role"])
