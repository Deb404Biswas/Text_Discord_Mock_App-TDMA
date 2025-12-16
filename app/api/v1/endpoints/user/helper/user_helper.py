from app.core.config.config import settings
from jose import jwt
from datetime import datetime, timezone
from app.services.database.database import db_service
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from typing import Annotated
from starlette import status
from passlib.context import CryptContext

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/auth/user-login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def user_authentication(user_id, user_password):
    user=await db_service.user_find_one(user_id)
    if not user:
        logger.warning(f"User with ID {user_id} not found in database")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not pwd_context.verify(user_password, user['user_password']):
        logger.warning(f"Incorrect password for user ID {user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return user

def create_access_token(user_name,user_id,expires_delta):
    encode = {
        "user_name": user_name,
        "user_id": user_id
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("user_name")
        user_id: str = payload.get("user_id")
        if user_name is None or user_id is None:
            logger.warning("Token payload missing user information")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"user_name": user_name, "user_id": user_id}
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired after 60 minutes")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTError:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
