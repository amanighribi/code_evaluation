from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Returns {"username": ..., "role": ...} or None. Never raises —
    endpoints decide whether authentication is required."""
    if credentials is None:
        return None
    return decode_access_token(credentials.credentials)


def require_teacher(current_user=Depends(get_current_user_optional)):
    """Dependency for endpoints restricted to teacher accounts."""
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Exam grading is available to teacher accounts only.",
        )
    return current_user
