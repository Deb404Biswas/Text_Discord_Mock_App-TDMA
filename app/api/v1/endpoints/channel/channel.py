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

try:
    @router.post('/{guild_id}/create-channel', status_code=status.HTTP_201_CREATED)
    @limiter.limit("10/minute")
    async def create_channel(request: Request,guild_id: str):
        # Simulate channel creation logic here
        logger.info("Channel created successfully")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Channel created successfully",
            "Channel_ID": ""
        }
except:
    logger.error("Failed to create channel at '/create-channel' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't create channel at the moment")

try:
    @router.delete('/{guild_id}/{channel_id}/delete-channel', status_code=status.HTTP_200_OK)
    @limiter.limit("10/minute")
    async def delete_channel(channel_id: str,guild_id: str, request: Request):
        # Simulate channel deletion logic here
        logger.info(f"Channel {channel_id} deleted successfully from guild {guild_id}")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Channel_ID: {channel_id} deleted successfully"
        }
except:
    logger.error("Failed to delete channel at '/{guild_id}/{channel_id}/delete-channel' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't delete channel at the moment")

try:
    @router.put('/{guild_id}/{channel_id}/rename-channel',status_code=status.HTTP_202_ACCEPTED)
    @limiter.limit("5/minute")
    async def rename_channel(channel_id: str,guild_id: str, new_channel_name: str, request: Request):
        # Simulate channel renaming logic here
        logger.info(f"Channel_ID:{channel_id} renamed to {new_channel_name} successfully in guild {guild_id}")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Channel_ID: {channel_id} renamed to {new_channel_name} successfully"
        }
except:
    logger.error("Failed to rename channel at '/{guild_id}/{channel_id}/rename-channel' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't rename channel at the moment")

try:
    @router.get('/{guild_id}/{channel_id}/display-messages', status_code=status.HTTP_200_OK)
    @limiter.limit("15/minute")
    async def display_messages(channel_id: str,guild_id: str, request: Request):
        # Simulate fetching channel messages logic here
        logger.info(f"Messages from Channel_ID:{channel_id} in guild {guild_id} fetched successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Messages from Channel_ID: {channel_id} fetched successfully",
            "Messages": []
        }
except:
    logger.error("Failed to display messages at '/{guild_id}/{channel_id}/display-messages' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't display messages at the moment")

try:
    @router.put('/{guild_id}/{channel_id}/send-message', status_code=status.HTTP_200_OK)
    @limiter.limit("20/minute")
    async def send_message(channel_id: str,guild_id: str, message_content: str, request: Request):
        # Simulate sending message logic here
        logger.info(f"Message sent to Channel_ID:{channel_id} in guild {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Message sent to Channel_ID: {channel_id} successfully"
        }
except:
    logger.error("Failed to send message at '/{guild_id}/{channel_id}/send-message' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't send message at the moment")

try:
    @router.put('/{guild_id}/{channel_id}/delete-message', status_code=status.HTTP_200_OK)
    @limiter.limit("15/minute")
    async def delete_message(channel_id: str,guild_id: str, user_id: str, request: Request):
        # Simulate deleting message logic here
        logger.info(f"Message from User_ID:{user_id} deleted in Channel_ID:{channel_id} of guild {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Message from User_ID: {user_id} deleted successfully"
        }
except:
    logger.error("Failed to delete message at '/{guild_id}/{channel_id}/delete-message' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't delete message at the moment")

try:
    @router.get('/{guild_id}/{channel_id}/edit-message', status_code=status.HTTP_200_OK)
    @limiter.limit("10/minute")
    async def edit_message(channel_id: str,guild_id: str, user_id: str, new_content: str, request: Request):
        # Simulate editing message logic here
        logger.info(f"Message from User_ID:{user_id} edited in Channel_ID:{channel_id} of guild {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Message from User_ID: {user_id} edited successfully"
        }
except:
    logger.error("Failed to edit message at '/{guild_id}/{channel_id}/edit-message' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't edit message at the moment")