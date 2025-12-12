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
            user_collection=Text_Discord_Mock_App_db['Users']
            guild_collection=Text_Discord_Mock_App_db['Guilds']
            role_collection=Text_Discord_Mock_App_db['Roles']
            channel_collection=Text_Discord_Mock_App_db['Channels']
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
    
    # User Collection Methods--------------
    
    @staticmethod
    async def user_collection_insert_one(doc):
        try: 
            await user_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while inserting user into user collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while inserting user into user collection')
    @staticmethod
    async def user_collection_find_one(user_id):
        try:
            user=await user_collection.find_one({"_id":user_id})
            return user
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while fetching user from user collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while fetching user from user collection')
    @staticmethod
    async def user_collection_update_one(user_id,update_doc):
        try:
            await user_collection.update_one({"_id":user_id},update_doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while updating user in user collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while updating user in user collection')
    
    # Guild Collection Methods------------
    
    @staticmethod
    async def guild_collection_insert_one(doc):
        try: 
            await guild_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while inserting document into guild collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while inserting into guild collection')
    @staticmethod
    async def guild_collection_find_one(guild_id):
        try:
            guild=await guild_collection.find_one({"_id":guild_id})
            return guild
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while fetching guild from guild collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while fetching guild from guild collection')

    @staticmethod
    async def guild_collection_update_one(guild_id,update_doc):
        try:
            await guild_collection.update_one({"_id":guild_id},update_doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while updating guild in guild collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while updating guild in guild collection')
    
    @staticmethod
    async def guild_collection_delete_one(guild_id):    
        try:
            await guild_collection.delete_one({"_id":guild_id})
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while deleting guild from guild collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while deleting guild from guild collection')
    
    # Role Collection Methods------------
    
    @staticmethod
    async def role_collection_insert_one(doc):
        try: 
            await role_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while inserting document into role collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while inserting into role collection')
    
    @staticmethod
    async def role_collection_find_one(role_id):
        try:
            return await role_collection.find_one({"_id":role_id})
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while fetching role from role collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while fetching role from role collection')
    
    @staticmethod
    async def role_collection_update_one(role_id,update_doc):
        try:
            await role_collection.update_one({"_id":role_id},update_doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while updating role in role collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while updating role in role collection')
    
    # Channel Collection Methods------------
    
    @staticmethod
    async def channel_collection_insert_one(doc):
        try: 
            await channel_collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Error:{e}. Occurred while inserting document into channel collection")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Error while inserting into channel collection')
    