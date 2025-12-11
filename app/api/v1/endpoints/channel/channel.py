from fastapi import APIRouter,HTTPException, Request
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect

router = APIRouter(
    prefix="/channel/",
    tags=["Channel"]
)
limiter= Limiter(key_func=get_remote_address)