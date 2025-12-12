from fastapi import APIRouter,HTTPException, Request,Depends
from typing import Annotated
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect
import uuid
from app.api.v1.endpoints.user.helper.user_helper import get_current_user
from app.api.dependencies.permissions import Permission
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/roles/",
    tags=["Roles"]
)
limiter= Limiter(key_func=get_remote_address)
current_user=Annotated[dict, Depends(get_current_user)]

class RoleRequest(BaseModel):
    role_name: str
    permissions_list: List[str] = []
class AssignReq(BaseModel):
    role_id: str
    user_id: str
    
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
    
try:
    @router.post('/{guild_id}/create-role', status_code=status.HTTP_201_CREATED)
    @limiter.limit("10/minute")
    async def create_role(request: Request, guild_id: str,user:current_user,role_req: RoleRequest):
        if not role_check_manage_roles(user['user_id'], guild_id):
            logger.error(f"User with ID {user['user_id']} does not have permission to manage roles in guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to manage roles in the guild")
        role_id=str(uuid.uuid4())
        role_name=role_req.role_name
        permissions_list=role_req.permissions_list
        await isValidPermissions(permissions_list)
        doc={
            "_id":role_id,
            "role_name": role_name,
            "users":[],
            "permissions": permissions_list
        }
        await DatabaseConnect.role_collection_insert_one(doc)
        logger.info(f"Role created successfully with name {role_name},id {role_id} in guild {guild_id}")
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Role created successfully",
            "Role_ID": role_id
        }
except Exception as e:
    logger.error(f"Failed to create role at '/create-role' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't create role at the moment")

try:
    @router.put('/{guild_id}/assign-role', status_code=status.HTTP_202_ACCEPTED)
    @limiter.limit("10/minute")
    async def assign_role(guild_id: str, assign_req:AssignReq ,user:current_user,request: Request):
        if not isUserinGuild(user['user_id'], guild_id):
            logger.error(f"User{user['user_name']} with ID {user['user_id']} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User{user['user_id']} is not a member of the guild")
        if not role_check_manage_roles(user['user_id'], guild_id):
            logger.error(f"User with ID {user['user_id']} does not have permission to manage roles in guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to manage roles in the guild")
        role_id=assign_req.role_id
        user_id=assign_req.user_id
        user_doc= await isUserinGuild(user_id, guild_id)
        if not user_doc:
            logger.error(f"User with ID {user_id} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to assign role not found in the guild")
        roles_list=user_doc.get("roles", [])
        roles_list.append({"guild_id": guild_id, "role_id": role_id})
        update_doc={"$set": {"roles": roles_list}}
        await DatabaseConnect.user_collection_update_one(user_id,update_doc)
        role_doc=await DatabaseConnect.role_collection_find_one(role_id)
        user_list=role_doc.get("users", [])
        user_list.append(user_id)
        update_role_doc={"$set": {"users": user_list}}
        await DatabaseConnect.role_collection_update_one(role_id,update_role_doc)
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        roles_in_guild=guild_doc.get("roles_in_guild", [])
        if role_id not in roles_in_guild:
            roles_in_guild.append(role_id)
            update_guild_doc={"$set": {"roles_in_guild": roles_in_guild}}
            await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
        logger.info(f"Role_ID:{role_id} assigned to User_ID:{user_id} successfully in guild {guild_id}")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Role_ID: {role_id} assigned"
        }
except Exception as e:
    logger.error(f"Failed to assign role at '/guild_id/user_id/assign-role' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't assign role at the moment")

try:
    @router.put('/{guild_id}/{user_id}/update-role', status_code=status.HTTP_202_ACCEPTED)
    @limiter.limit("5/minute")
    async def update_role(user_id: str, guild_id: str, role_id: str,user:current_user, request: Request):
        # Simulate role update logic here
        logger.info(f"Role updated to Role_ID:{role_id} for User_ID:{user_id} successfully in guild {guild_id}")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Role updated for User_ID: {user_id} successfully"
        }
except Exception as e:
    logger.error(f"Failed to update role at '/guild_id/user_id/update-role' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't update role at the moment")

try:
    @router.get('/display-permissions', status_code=status.HTTP_200_OK)
    @limiter.limit("1/second")
    async def display_permissions(request: Request):
        # Simulate fetching permissions logic here
        logger.info("Permissions fetched successfully")
        return {
            "status": status.HTTP_200_OK,
            "message": "Permissions fetched successfully",
            "Permissions": []
        }
except Exception as e:
    logger.error(f"Failed to display permissions at '/display-permissions' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't display permissions at the moment")