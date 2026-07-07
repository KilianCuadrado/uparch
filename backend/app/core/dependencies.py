from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_token

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=403, detail="Token faltante")

    user = verify_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

    return user
