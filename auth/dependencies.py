from fastapi import Header
from auth.security import decode_access_token


def get_current_user_optional(authorization: str = Header(default=None)) -> str | None:
    """Extracts the username from a Bearer token in the Authorization header.
    Returns None if no token is provided or it's invalid — does NOT raise an error,
    since /analyze should still work without login (just without history tracking)."""

    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()
    username = decode_access_token(token)
    return username


if __name__ == "__main__":
    from auth.security import create_access_token

    valid_token = create_access_token("amani")
    print("Valid token result:", get_current_user_optional(f"Bearer {valid_token}"))
    print("No header result:", get_current_user_optional(None))
    print("Malformed header result:", get_current_user_optional("NotBearer xyz"))
    print("Invalid token result:", get_current_user_optional("Bearer not.a.real.token"))