import re
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from app.models import users_db
from app.rate_limiter import rate_increase, rate_decrease
from app.auth import create_access_token, verify_access_token
import jwt
import logging
from logging.config import dictConfig

app = FastAPI(title="Secure API Gateway Project")
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "logs/app.log",
            "encoding": "utf-8",
            "mode": "a"
        },
    },
    "loggers": {
        "app": {"handlers": ["default", "file_handler"], "level": "DEBUG", "propagate": False},
    },
}

dictConfig(log_config)

logger = logging.getLogger("app")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    token: str

current_user = None

@app.get("/")
def home():
    logger.info("Home endpoint accessed")
    return {"message": "Secure API Gateway is running"}


@app.get("/public")
def public_route():
    logger.info("Public endpoint accessed")
    return {"message": "This is a public endpoint"}


@app.post("/login")
def login(data: LoginRequest):
    logger.info("Login requested for user: %s", data.username)
    rate_increase()
    global current_user
    user = users_db.get(data.username)
    current_user = data.username

    if re.match(r"^[a-zA-Z0-9_]+$", data.username) is None:
        rate_decrease()
        logger.warning("Invalid username format: %s", data.username)
        raise HTTPException(status_code=400, detail="Invalid username format")
    if re.match(r"^[a-zA-Z0-9_]+$", data.password) is None:
        rate_decrease()
        logger.warning("Invalid password format: %s", data.password)
        raise HTTPException(status_code=400, detail="Invalid password format")
    
    if not user or user["password"] != data.password:
        logger.warning("Failed login attempt for user: %s", data.username)
        rate_decrease()
        raise HTTPException(status_code=401, detail="Invalid username or password")


    token = create_access_token(data.username, user["role"])
    rate_decrease()
    logger.info("User %s logged in successfully", data.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@app.post("/protected")
def protected_route(data: TokenRequest):
    rate_increase()
    token = data.token

    try:
        payload = verify_access_token(token)
        user = users_db.get(payload["sub"])
        if not user or str(user["role"]) != "admin":
            rate_decrease()
            logger.warning("Access forbidden for user: %s with role: %s", payload["sub"], user["role"] if user else "unknown")
            raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
        
        rate_decrease()
        logger.info("Access granted for user: %s with role: %s", payload["sub"], payload["role"])
        return {
            "message": "Access granted",
            "user": payload["sub"],
            "role": payload["role"]
        }
    except jwt.ExpiredSignatureError:
        rate_decrease()
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        rate_decrease()
        logger.warning("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")