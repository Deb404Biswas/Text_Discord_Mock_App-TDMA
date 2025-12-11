from fastapi import APIRouter,HTTPException, Request
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect

router = APIRouter(
    prefix="/guild/",
    tags=["Guild"]
)
limiter= Limiter(key_func=get_remote_address)
try:
    @router.post('/create-guild', status_code=status.HTTP_201_CREATED)
    @limiter.limit("5/minute")
    async def create_guild(request: Request):
        # Simulate guild creation logic here
        logger.info("Guild created successfully")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Guild created successfully",
            "Guild_ID": ""
        }
except:
    logger.error("Failed to create guild at '/create-guild' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't create guild at the moment")

try:
    @router.delete('/{guild_id}/delete-guild', status_code=status.HTTP_200_OK)
    @limiter.limit("5/minute")
    async def delete_guild(guild_id: str, request: Request):
        # Simulate guild deletion logic here
        logger.info(f"Guild {guild_id} deleted successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Guild_ID: {guild_id} deleted successfully"
        }
except:
    logger.error("Failed to delete guild at '/{guild_id}/delete-guild' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't delete guild at the moment")

try:
    @router.put('/{guild_id}/trasfer-owner',status_code=status.HTTP_202_ACCEPTED)
    @limiter.limit("3/minute")
    async def transfer_guild_ownership(guild_id: str, new_owner_id: str, request: Request):
        # Simulate guild ownership transfer logic here
        logger.info(f"Guild_ID:{guild_id} ownership transferred to user {new_owner_id} successfully")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Guild_ID: {guild_id} ownership transferred to User_ID: {new_owner_id} successfully"
        }
except:
    logger.error("Failed to transfer guild ownership at '/{guild_id}/transfer-owner' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't transfer guild ownership at the moment")

try:
    @router.get('/{guild_id}/guild-details', status_code=status.HTTP_200_OK)
    @limiter.limit("10/minute")
    async def get_guild_info(guild_id: str, request: Request):
        # Simulate fetching guild information logic here
        logger.info(f"Fetched information for Guild_ID: {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Fetched information for Guild_ID: {guild_id} successfully",
            "guild_info": {}
        }
except:
    logger.error("Failed to fetch guild information at '/{guild_id}/info' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't fetch guild information at the moment")

try:
    @router.put('/{guild_id}/update-guild-name', status_code=status.HTTP_200_OK)
    @limiter.limit("5/minute")
    async def update_guild_name(guild_id: str, new_name: str, request: Request):
        # Simulate guild name update logic here
        logger.info(f"Guild_ID: {guild_id} name updated to {new_name} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Guild_ID: {guild_id} name updated to {new_name} successfully"
        }
except:
    logger.error("Failed to update guild name at '/{guild_id}/update-guild-name' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't update guild name at the moment")