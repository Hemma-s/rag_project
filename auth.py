import os, time, hmac
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = os.environ.get("JWT_SECRET")
if not SECRET or len(SECRET) < 32:
    raise RuntimeError("Set JWT_SECRET to a random string of at least 32 characters")
ALGO = "HS256"

# just a demo
USERS = {
    "alice": {"password": "alice123", "tenant_id": "acme",    "role": "admin"},
    "bob":   {"password": "bob123",   "tenant_id": "acme",    "role": "employee"},
    "erin":  {"password": "erin123",  "tenant_id": "globex",  "role": "admin"},
    "carol": {"password": "carol123", "tenant_id": "globex",  "role": "employee"},
    "frank": {"password": "frank123", "tenant_id": "initech", "role": "admin"},
    "dave":  {"password": "dave123",  "tenant_id": "initech", "role": "employee"},
}

bearer = HTTPBearer()


def authenticate(username, password):
    u = USERS.get(username)
    if u and hmac.compare_digest(u["password"], password):
        return {"user_id": username, "tenant_id": u["tenant_id"], "role": u["role"]}
    return None


def create_token(user):
    payload = {**user, "exp": int(time.time()) + 3600}  # valid for 1 hour
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        d = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": d["user_id"], "tenant_id": d["tenant_id"], "role": d["role"]}