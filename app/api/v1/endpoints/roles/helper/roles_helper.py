from app.services.database.database import DatabaseConnect
from fastapi import HTTPException,status
from loguru import logger
from app.api.dependencies.permissions import Permission

async def isValidPermissions(permissions_list):
    for perm in permissions_list:
        if perm not in Permission.__members__:
            logger.error(f"Invalid permission: {perm}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid permission: {perm}")
    
async def role_check_manage_roles(user_id, guild_id):
    user_doc = await DatabaseConnect.user_collection_find_one(user_id)
    roles=user_doc.get("roles", [])
    for role in roles:
        if role['guild_id'] == guild_id:
            role_id=role['role_id']
            break
    role_doc=await DatabaseConnect.role_collection_find_one(role_id)
    permissions_list=role_doc.get("permissions", [])
    for perm in permissions_list:
        if perm == 'manage_roles':
            return True
    return False

async def isUserinGuild(user_id, guild_id):
    guild = await DatabaseConnect.guild_collection_find_one(guild_id)
    if not guild:
        logger.error(f"Guild with ID {guild_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
    if user_id in guild['users']:
        user_doc = await DatabaseConnect.user_collection_find_one(user_id)
        return user_doc
    else:
        logger.error(f"User with ID {user_id} is not a member of guild {guild_id}")
        return None
    
async def userValidCheck(user_name,user_id,guild_id):
    if not isUserinGuild(user_id, guild_id):
        logger.error(f"User{user_name} with ID {user_id} is not a member of guild {guild_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User{user_id} is not a member of the guild")
    if not role_check_manage_roles(user_id, guild_id):
        logger.error(f"User with ID {user_id} does not have permission to manage roles in guild {guild_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to manage roles in the guild")
    return True