import re
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from app.models import users_db
from rate_limiter import rate_increase, rate_decrease
from app.auth import create_access_token, verify_access_token
import jwt

app = FastAPI(title="Secure API Gateway Project")


class LoginRequest(BaseModel):
    username: str
    password: str

current_user = None
@app.get("/")
def home():
    return {"message": "Secure API Gateway is running"}


@app.get("/public")
def public_route():
    return {"message": "This is a public endpoint"}


@app.post("/login")
def login(data: LoginRequest):
    rate_increase()
    global current_user
    user = users_db.get(data.username)
    current_user = data.username

    if re.match(r"^[a-zA-Z0-9_]+$", data.username) is None:
        rate_decrease()
        raise HTTPException(status_code=400, detail="Invalid username format")
    if re.match(r"^[a-zA-Z0-9_]+$", data.password) is None:
        rate_decrease()
        raise HTTPException(status_code=400, detail="Invalid password format")
    
    if not user or user["password"] != data.password:
        rate_decrease()
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data.username, user["role"])
    rate_decrease()
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@app.get("/protected")
def protected_route(authorization: str = Header(None)):
    rate_increase()
    global current_user
    user = users_db.get(current_user)

    if str(user["role"]) != "admin":
        rate_decrease()
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
        
    if not authorization or not authorization.startswith("Bearer "):
        rate_decrease()
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = verify_access_token(token)
        rate_decrease()
        return {
            "message": "Access granted",
            "user": payload["sub"],
            "role": payload["role"]
        }
    except jwt.ExpiredSignatureError:
        rate_decrease()
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        rate_decrease()
        raise HTTPException(status_code=401, detail="Invalid token")