from fastapi import Header, HTTPException, Depends
from typing import Optional

# Simple token -> role map for PoC. Replace with real auth in production.
TOKENS = {
    "admin-token": {"role": "admin", "name": "admin"},
    "attendant-token": {"role": "attendant", "name": "attendant"},
}

def get_current_user(authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    if not token and x_api_key:
        token = x_api_key
    if not token or token not in TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return TOKENS[token]

def require_role(required: str):
    def _dependency(user=Depends(get_current_user)):
        if user.get("role") != required:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dependency
