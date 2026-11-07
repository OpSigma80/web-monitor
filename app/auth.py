import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings


security = HTTPBasic()


def require_api_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username_valid = secrets.compare_digest(credentials.username, settings.api_username)
    password_valid = secrets.compare_digest(credentials.password, settings.api_password)

    if not (username_valid and password_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
