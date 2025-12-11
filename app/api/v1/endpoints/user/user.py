from fastapi import APIRouter,HTTPException,Request
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect

router = APIRouter(
    prefix="/user/",
    tags=["User"]
)

limiter = Limiter(key_func=get_remote_address)
try:
    @router.post('/user-register', status_code=status.HTTP_201_CREATED)
    @limiter.limit("10/minute")
    async def register_user(request: Request):
        # Simulate user registration logic here
        logger.info("User registered successfully")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User registered successfully"
        }
except:
    logger.error("Failed to register user")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't register user at the moment")