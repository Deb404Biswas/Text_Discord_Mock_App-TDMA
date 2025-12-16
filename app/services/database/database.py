from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from loguru import logger
from starlette import status
from app.core.config.config import settings

class DatabaseService:
    def __init__(self):
        self.client = None
        self.user_collection = None
        self.guild_collection = None
        self.role_collection = None
        self.channel_collection = None
    
    async def connect(self):
        try:
            connection_string = settings.MONGO_CONNECTION_URI
            self.client = AsyncIOMotorClient(connection_string)
            db = self.client['Text_Discord_Mock_App']
            
            self.user_collection = db['Users']
            self.guild_collection = db['Guilds']
            self.role_collection = db['Roles']
            self.channel_collection = db['Channels']
            
            await self.client.admin.command("ping")
            logger.info("MongoDB connection established.")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='MongoDB connection failed'
            )
            
    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    # User operations
    async def user_insert_one(self, doc):
        try:
            await self.user_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while inserting user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while inserting user'
            )
    
    async def user_find_one(self, user_id):
        try:
            return await self.user_collection.find_one({"_id": user_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while fetching user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while fetching user'
            )
    
    async def user_update_one(self, user_id, update_doc):
        try:
            await self.user_collection.update_one({"_id": user_id}, update_doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while updating user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while updating user'
            )
    
    # Guild operations
    async def guild_insert_one(self, doc):
        try:
            await self.guild_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while inserting guild")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while inserting guild'
            )
    
    async def guild_find_one(self, guild_id):
        try:
            return await self.guild_collection.find_one({"_id": guild_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while fetching guild")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while fetching guild'
            )
    
    async def guild_update_one(self, guild_id, update_doc):
        try:
            await self.guild_collection.update_one({"_id": guild_id}, update_doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while updating guild")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while updating guild'
            )
    
    async def guild_delete_one(self, guild_id):
        try:
            await self.guild_collection.delete_one({"_id": guild_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while deleting guild")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while deleting guild'
            )
    
    # Role operations
    async def role_insert_one(self, doc):
        try:
            await self.role_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while inserting role")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while inserting role'
            )
    
    async def role_find_one(self, role_id):
        try:
            role_doc=await self.role_collection.find_one({"_id": role_id})
            logger.debug(f"role_doc:{role_doc},role_id:{role_id}")
            return role_doc
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while fetching role")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while fetching role'
            )
    
    async def role_update_one(self, role_id, update_doc):
        try:
            await self.role_collection.update_one({"_id": role_id}, update_doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while updating role")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while updating role'
            )
    
    async def role_delete_one(self, role_id):
        try:
            await self.role_collection.delete_one({"_id": role_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while deleting role")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while deleting role'
            )
    
    # Channel operations
    async def channel_insert_one(self, doc):
        try:
            await self.channel_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while inserting channel")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while inserting channel'
            )
    
    async def channel_find_one(self, channel_id):
        try:
            return await self.channel_collection.find_one({"_id": channel_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while fetching channel")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while fetching channel'
            )
    
    async def channel_update_one(self, channel_id, update_doc):
        try:
            await self.channel_collection.update_one({"_id": channel_id}, update_doc)
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while updating channel")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while updating channel'
            )
    
    async def channel_delete_one(self, channel_id):
        try:
            await self.channel_collection.delete_one({"_id": channel_id})
        except Exception as e:
            logger.error(f"Error: {e}. Occurred while deleting channel")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error while deleting channel'
            )

db_service = DatabaseService()

async def get_db() -> DatabaseService:
    return db_service
