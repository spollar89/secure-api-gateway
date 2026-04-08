from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from app.models import users_db
from app.auth import create_access_token, verify_access_token
import jwt

app = FastAPI(title="Secure API Gateway Project")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {"message": "Secure API Gateway is running"}


@app.get("/public")
def public_route():
    return {"message": "This is a public endpoint"}


@app.post("/login")
def login(data: LoginRequest):
    user = users_db.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data.username, user["role"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@app.get("/protected")
def protected_route(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = verify_access_token(token)
        return {
            "message": "Access granted",
            "user": payload["sub"],
            "role": payload["role"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")