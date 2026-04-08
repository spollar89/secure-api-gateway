import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

def create_access_token(username: str, role: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])