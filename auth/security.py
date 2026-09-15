import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production-1a2b3c")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")[:72]  # bcrypt's own hard limit
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """Returns the username if the token is valid, None otherwise."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


if __name__ == "__main__":
    hashed = hash_password("my_test_password")
    print("Hashed:", hashed)
    print("Verify correct password:", verify_password("my_test_password", hashed))
    print("Verify wrong password:", verify_password("wrong_password", hashed))

    token = create_access_token("amani")
    print("\nToken:", token)
    print("Decoded username:", decode_access_token(token))
    print("Invalid token decode:", decode_access_token("not.a.real.token"))