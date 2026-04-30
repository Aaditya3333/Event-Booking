from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Optional
import hashlib
import secrets
import json
from datetime import datetime, timedelta

# Simple in-memory user storage (for testing only)
USERS: Dict[str, Dict] = {}
TOKENS: Dict[str, Dict] = {}

router = APIRouter()
security = HTTPBearer()

class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    created_at: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    TOKENS[token] = {
        "user_id": user_id,
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token

def get_user_from_token(token: str) -> Optional[Dict]:
    if token not in TOKENS:
        return None
    
    token_data = TOKENS[token]
    if datetime.now() > token_data["expires_at"]:
        del TOKENS[token]
        return None
    
    return USERS.get(token_data["user_id"])

@router.post("/register")
async def register(user_data: UserCreate):
    # Check if user already exists
    for user in USERS.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if user["username"] == user_data.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    user_id = secrets.token_urlsafe(16)
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "password_hash": hashed_password,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    USERS[user_id] = user
    
    # Create access token
    access_token = create_access_token(user_id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "is_active": user["is_active"],
            "created_at": user["created_at"]
        }
    }

@router.post("/login")
async def login(login_data: UserLogin):
    # Find user by email
    user = None
    for u in USERS.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(user["id"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "is_active": user["is_active"],
            "created_at": user["created_at"]
        }
    }

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user["full_name"],
        "phone": user["phone"],
        "is_active": user["is_active"],
        "created_at": user["created_at"]
    }

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token in TOKENS:
        del TOKENS[token]
    return {"message": "Successfully logged out"}
