import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.db.init import init_db
from app.core.security import create_access_token, verify_token
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()
bearer_auth = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str


def get_verified_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_auth)):
    user = verify_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    token = create_access_token(request.username)
    return LoginResponse(token=token, username=request.username)


@router.post("/auth/register", status_code=201)
async def register(request: LoginRequest):
    init_db()
    try:
        register_user(request.username, request.password)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    return {"message": "Usuario creado", "username": request.username}


@router.post("/auth/login", deprecated=True)
async def auth_login(request: LoginRequest):
    # Ruta heredada para compatibilidad con clientes existentes.
    # Nuevos clientes deben usar /login.
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return {"access_token": create_access_token(request.username)}


@router.get("/verify")
async def verify(user: dict = Depends(get_verified_user)):
    return {
        "message": "Token válido",
        "mensaje": "Token válido",
        "username": user["username"],
        "user_id": user["id"],
    }
