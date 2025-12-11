from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config.config import settings
from fastapi import HTTPException
from loguru import logger
from starlette import status

client=None
user_collection=None
guild_collection=None
role_collection=None
channel_collection=None

class DatabaseConnect:
    @staticmethod
    async def fetch_mongo_connection():
        global client, user_collection, guild_collection, role_collection, channel_collection
        try:
            mongo_password = settings.MONGO_PASS
            connection_string = f"mongodb+srv://Debdwaipayan:{mongo_password}@internship.3kcwior.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true&appName=Internship"
            client =AsyncIOMotorClient(connection_string)
            Text_Discord_Mock_App_db=client['Text_Discord_Mock_App']
            user_collection=Text_Discord_Mock_App_db['user']
            guild_collection=Text_Discord_Mock_App_db['Guild']
            role_collection=Text_Discord_Mock_App_db['Role']
            channel_collection=Text_Discord_Mock_App_db['Channel']
            await client.admin.command("ping")
            logger.info("MongoDB connection established.")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='MongoDB connection failed')
    @staticmethod
    async def close_mongo_connection():
        try:
            client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while closing mongodb connection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while closing MongoDB connection')