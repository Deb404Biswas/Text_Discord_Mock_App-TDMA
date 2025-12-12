from fastapi import APIRouter,HTTPException, Request,Depends
from typing import Annotated
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect
from app.api.v1.endpoints.user.helper.user_helper import get_current_user
from app.api.dependencies.permission.permissions import Permission
from app.api.v1.endpoints.guild.helper.guild_helper import *
from app.core.config.config import settings
import uuid
import datetime


router = APIRouter(
    prefix="/guild/",
    tags=["Guild"]
)
limiter= Limiter(key_func=get_remote_address)
current_user=Annotated[dict, Depends(get_current_user)]

try:
    @router.post('/create-guild', status_code=status.HTTP_201_CREATED)
    @limiter.limit("5/minute")
    async def create_guild(request: Request,user:current_user,guild_name:str):
        if not await DatabaseConnect.user_collection_find_one(user['user_id']):
            logger.error(f"User with ID {user['user_id']} not found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{user['user_name']} not found")
        guild_id=str(uuid.uuid4())
        doc={
            "_id":guild_id,
            "guild_name": guild_name,
            "creator_id": user['user_id'],
            "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "owner_id": user['user_id'],
            "users": [user['user_id']],
            "roles_in_guild": [f'{settings.OWNER_ROLE_ID}'],
            "channels": []
        }
        await DatabaseConnect.guild_collection_insert_one(doc)
        logger.info("Guild created successfully")
        user_doc=await DatabaseConnect.user_collection_find_one(user['user_id'])
        user_guilds=user_doc.get("guilds", [])
        user_guilds.append(guild_id)
        user_roles=user_doc.get("roles", [])
        user_roles.append({"guild_id": guild_id, "role_id": f'{settings.OWNER_ROLE_ID}'})
        update_user_doc={
            "$set": {
                "guilds": user_guilds,
                "roles": user_roles
            }
        }
        await DatabaseConnect.user_collection_update_one(user['user_id'],update_user_doc)
        role_doc=await DatabaseConnect.role_collection_find_one(f'{settings.OWNER_ROLE_ID}')
        user_list=role_doc.get("users", [])
        user_list.append(user['user_id'])
        update_role_doc={
            "$set": {
                "users": user_list
            }
        }   
        await DatabaseConnect.role_collection_update_one(f'{settings.OWNER_ROLE_ID}',update_role_doc)
        logger.info(f"User {user['user_id']} added as owner to guild {guild_id}")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Guild created successfully",
            "Guild_ID": guild_id
        }
except:
    logger.error("Failed to create guild at '/create-guild' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't create guild at the moment")

try:
    @router.delete('/{guild_id}/delete-guild', status_code=status.HTTP_200_OK)
    @limiter.limit("5/minute")
    async def delete_guild(guild_id: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        await ValidUserCheck(user_id,user_name,guild_id,"guild_owner")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        user_list=guild_doc.get("users", [])
        for user_id in user_list:
            user_doc=await DatabaseConnect.user_collection_find_one(user_id)
            user_guilds=user_doc.get("guilds", [])
            user_roles=user_doc.get("roles", [])
            for user_role in user_roles:
                if user_role['guild_id'] == guild_id:
                    role_id=user_role['role_id']
                    user_roles.remove(user_role)
                    role_doc=await DatabaseConnect.role_collection_find_one(role_id)
                    role_users=role_doc.get("users", [])
                    role_users.remove(user_id)
                    update_role_doc={
                        "$set": {
                            "users": role_users
                        }
                    }
                    await DatabaseConnect.role_collection_update_one(role_id,update_role_doc)
                    break
            user_guilds.remove(guild_id)
            update_user_doc={
                "$set": {
                    "guilds": user_guilds,
                    "roles": user_roles
                }
            }
            await DatabaseConnect.user_collection_update_one(user_id,update_user_doc)
        await DatabaseConnect.guild_collection_delete_one(guild_id)
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
    async def transfer_guild_ownership(guild_id: str, new_owner_id: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        await ValidUserCheck(user_id,user_name,guild_id,"guild_owner")
        user_doc=await isUserinGuild(new_owner_id, guild_id)
        if not user_doc:
            logger.error(f"New owner with ID {new_owner_id} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="New owner must be a member of the guild")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        update_guild_doc={
            "$set": {
                "owner_id": new_owner_id
            }
        }
        user_roles=user_doc.get("roles", [])
        for user_role in user_roles:
            if user_role['guild_id'] == guild_id:
                user_role['role_id']=f'{settings.OWNER_ROLE_ID}'
                break
        logger.debug(f"Updated user roles: {user_roles}")
        update_user_doc={
            "$set": {
                "roles": user_roles
            }
        }
        await DatabaseConnect.user_collection_update_one(new_owner_id,update_user_doc)
        await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
        role_doc=await DatabaseConnect.role_collection_find_one(f'{settings.OWNER_ROLE_ID}')
        users_list=role_doc.get("users", [])
        for role_user_id in users_list:
            if role_user_id==user_id:
                users_list.remove(role_user_id)
                users_list.append(new_owner_id)
                update_role_doc={
                    "$set": {
                        "users": users_list
                    }
                }
                await DatabaseConnect.role_collection_update_one(f'{settings.OWNER_ROLE_ID}',update_role_doc)
                break
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
    async def get_guild_info(guild_id: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        user_doc=await isUserinGuild(user_id, guild_id)
        if not user_doc:
            logger.error(f"User{user_name} with ID {user_id} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User{user_id} is not a member of the guild")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        logger.info(f"Fetched information for Guild_ID: {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Fetched information for Guild_ID: {guild_id} successfully",
            "guild_info": guild_doc
        }
except:
    logger.error("Failed to fetch guild information at '/{guild_id}/info' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't fetch guild information at the moment")

try:
    @router.put('/{guild_id}/update-guild-name', status_code=status.HTTP_200_OK)
    @limiter.limit("5/minute")
    async def update_guild_name(guild_id: str, new_guild_name: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        await ValidUserCheck(user_id,user_name,guild_id,"mod_guild")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        guild_doc['guild_name']=new_guild_name
        update_guild_doc={
            "$set": {
                "guild_name": new_guild_name
            }   
        }
        await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
        logger.info(f"Guild_ID: {guild_id} name updated to {new_guild_name} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"Guild_ID: {guild_id} name updated to {new_guild_name} successfully"
        }
except:
    logger.error("Failed to update guild name at '/{guild_id}/update-guild-name' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't update guild name at the moment")

try:
    @router.put("/{guild_id}/add-user", status_code=status.HTTP_200_OK)
    @limiter.limit("10/minute")
    async def add_user_to_guild(guild_id: str, new_member_user_id: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        await ValidUserCheck(user_id,user_name,guild_id,"add_guild")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        users_list=guild_doc.get("users", [])
        for user_id in users_list:
            if user_id==new_member_user_id:
                logger.error(f"User with ID {new_member_user_id} is already a member of guild {guild_id}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of the guild")
        users_list.append(new_member_user_id)
        update_guild_doc={ 
            "$set": {
                "users": users_list
            }
        }
        await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
        user_doc=await DatabaseConnect.user_collection_find_one(new_member_user_id)
        user_guilds=user_doc.get("guilds", [])
        user_roles=user_doc.get("roles", [])
        user_guilds.append(guild_id)
        user_roles.append({"guild_id": guild_id, "role_id": f'{settings.MEMBER_ROLE_ID}'})
        update_user_doc={
            "$set": {
                "guilds": user_guilds,
                "roles": user_roles
            }
        }
        await DatabaseConnect.user_collection_update_one(new_member_user_id,update_user_doc)
        role_doc=await DatabaseConnect.role_collection_find_one(f'{settings.MEMBER_ROLE_ID}')
        role_users=role_doc.get("users", [])
        role_users.append(new_member_user_id)
        update_role_doc={
            "$set": {
                "users": role_users
            }
        }
        await DatabaseConnect.role_collection_update_one(f'{settings.MEMBER_ROLE_ID}',update_role_doc)
        logger.info(f"User_ID: {user_id} added to Guild_ID: {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"User_ID: {user_id} added to Guild_ID: {guild_id} successfully"
        }
except:
    logger.error("Failed to add user to guild at '/{guild_id}/add-user' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't add user to guild at the moment")

try:
    @router.put("/{guild_id}/remove-user", status_code=status.HTTP_200_OK)
    @limiter.limit("10/minute")
    async def remove_user_from_guild(guild_id: str, member_user_id: str, request: Request,user:current_user):
        user_id=user['user_id']
        user_name=user['user_name']
        await ValidUserCheck(user_id,user_name,guild_id,"kick_member")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        user_list=guild_doc.get("users", [])
        if member_user_id not in user_list:
            logger.error(f"User with ID {member_user_id} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a member of the guild")
        user_list.remove(member_user_id)
        update_guild_doc={
            "$set": {
                "users": user_list
            }
        }
        await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
        user_doc=await DatabaseConnect.user_collection_find_one(member_user_id)
        user_guilds=user_doc.get("guilds", [])
        user_roles=user_doc.get("roles", [])
        for user_role in user_roles:
            if user_role['guild_id'] == guild_id:
                role_id=user_role['role_id']
                user_roles.remove(user_role)
                role_doc=await DatabaseConnect.role_collection_find_one(role_id)
                role_users=role_doc.get("users", [])
                role_users.remove(member_user_id)
                update_role_doc={
                    "$set": {
                        "users": role_users
                    }
                }
                await DatabaseConnect.role_collection_update_one(role_id,update_role_doc)
                break
            user_guilds.remove(guild_id)
        update_user_doc={
            "$set": {
                "guilds": user_guilds,
                "roles": user_roles
            }
        }
        await DatabaseConnect.user_collection_update_one(member_user_id,update_user_doc)
        logger.info(f"User_ID: {member_user_id} removed from Guild_ID: {guild_id} successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": f"User_ID: {member_user_id} removed from Guild_ID: {guild_id} successfully"
        }
except:
    logger.error("Failed to remove user from guild at '/{guild_id}/remove-user' endpoint")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't remove user from guild at the moment")