from fastapi import APIRouter
from app.api.v1.endpoints.user.user import router as user_router
from app.api.v1.endpoints.channel.channel import router as channel_router
from app.api.v1.endpoints.guild.guild import router as guild_router
from app.api.v1.endpoints.roles.roles import router as roles_router
router = APIRouter(
    prefix="/v1",
)
router.include_router(user_router)
router.include_router(channel_router)
router.include_router(guild_router)
router.include_router(roles_router)