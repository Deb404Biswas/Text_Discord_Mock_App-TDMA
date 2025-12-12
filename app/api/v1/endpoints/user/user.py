from fastapi import APIRouter,HTTPException,Request,Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Annotated
from starlette import status
from loguru import logger
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect
from app.api.v1.endpoints.user.schema.user_schema import Token, UserRequest
from app.api.v1.endpoints.user.helper.user_helper import user_authentication, create_access_token

router = APIRouter(
    prefix="/user/",
    tags=["User"]
)
limiter = Limiter(key_func=get_remote_address)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

try:
    @router.post('/user-register', status_code=status.HTTP_201_CREATED)
    @limiter.limit("10/minute")
    async def register_user(request: Request, user_req:UserRequest):
        doc={
            "_id": user_req.user_id,
            "user_name": user_req.user_name,
            "user_password": pwd_context.hash(user_req.user_password),
            "guilds": [],
            "roles": []
        }
        await DatabaseConnect.user_collection_insert_one(doc)
        logger.info("User registered successfully")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User registered successfully"
        }
except:
    logger.error("Failed to register user")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't register user at the moment")

try:
    @router.post('/auth/user-login', response_model=Token)
    @limiter.limit("15/minute")
    async def login_user(request: Request,form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        user_name = form_data.username
        user_id = form_data.client_id
        user_password = form_data.password
        user = await user_authentication(user_id,user_password)
        if not user:
            logger.warning("Invalid credentials provided")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(user_name, user_id,timedelta(minutes=60))
        logger.info("User logged in successfully")
        return {
            "access_token": token,
            "token_type": "bearer"
        }
except Exception as e:
    logger.error(f"An error occurred: {e} at /auth/user-login enpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred")