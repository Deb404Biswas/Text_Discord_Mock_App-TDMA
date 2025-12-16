from fastapi import APIRouter,HTTPException, Request,Depends
from typing import Annotated
from starlette import status
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.database.database import DatabaseConnect
import uuid
from app.api.v1.endpoints.user.helper.user_helper import get_current_user
from app.api.dependencies.permission.permissions import Permission
from app.api.v1.endpoints.roles.schema.roles_schema import *
from app.api.v1.endpoints.roles.helper.roles_helper import *

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)
limiter= Limiter(key_func=get_remote_address)
current_user=Annotated[dict, Depends(get_current_user)]

try:
    @router.post('/{guild_id}/create-role', status_code=status.HTTP_201_CREATED)
    @limiter.limit("10/minute")
    async def create_role(request: Request, guild_id: str,user:current_user,role_req: RoleRequest):
        if not await userValidCheck(user['user_name'],user['user_id'],guild_id):
            return
        role_id=str(uuid.uuid4())
        role_name=role_req.role_name
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        roles_list=guild_doc.get("roles_in_guild", [])
        if role_name in roles_list:
            HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Role with name {role_name} already exists.")
        permissions_list=role_req.permissions_list
        await isValidPermissions(permissions_list)
        permissions_list.extend(["read_msg", "write_msg", "delete_msg", "edit_msg"])
        doc={
            "_id":role_id,
            "role_name": role_name,
            "permissions": permissions_list
        }
        await DatabaseConnect.role_collection_insert_one(doc)
        roles_list.append(role_id)
        update_guild_doc={"$set": 
            {"roles_in_guild": roles_list}
        }
        await DatabaseConnect.guild_collection_update_one(guild_id,update_guild_doc)
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
        if not await userValidCheck(user['user_name'],user['user_id'],guild_id):
            return
        role_id=assign_req.role_id
        user_id=assign_req.user_id
        user_doc= await isUserinGuild(user_id, guild_id)
        if not user_doc:
            logger.error(f"User with ID {user_id} is not a member of guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to assign role not found in the guild")
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        guild_roles=guild_doc.get("roles_in_guild",[])
        if role_id not in guild_roles:
            logger.info(f"role id {role_id} not present in guild id {guild_id}")
            HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Role id not present in guild")
        user_roles=user_doc.get("roles",[])
        for user_role in user_roles:
            if user_role["guild_id"]==guild_id:
                if user_role["role_id"]==role_id:
                    logger.info(f"role id: {role_id} already assigned to user id: {user_id}")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Role already assigned to user")
                user_role["role_id"]=role_id
                update_user_doc={"$set": 
                    {"roles": user_roles}
                }
                await DatabaseConnect.user_collection_update_one(user_id,update_user_doc)
                break
        logger.info(f"Role_ID:{role_id} assigned to User_ID:{user_id} successfully in guild {guild_id}")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Role_ID: {role_id} assigned"
        }
except Exception as e:
    logger.error(f"Failed to assign role at '/guild_id/user_id/assign-role' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't assign role at the moment")

try:
    @router.put('/{guild_id}/update-role', status_code=status.HTTP_202_ACCEPTED)
    @limiter.limit("5/minute")
    async def update_role(guild_id: str, role_id: str,user:current_user, request: Request,role_req: RoleRequest):
        if not await userValidCheck(user['user_name'],user['user_id'],guild_id):
            return
        guild_doc=await DatabaseConnect.guild_collection_find_one(guild_id)
        guild_roles=guild_doc.get("roles_in_guild", [])
        if role_id not in guild_roles:
            logger.error(f"Role with ID {role_id} not found in guild {guild_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found in the guild")
        role_doc=await DatabaseConnect.role_collection_find_one(role_id)
        if not role_doc:
            logger.error(f"Role with ID {role_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        role_name=role_req.role_name
        for guild_role in guild_roles:
            guild_role_doc=await DatabaseConnect.role_collection_find_one(guild_role)
            if guild_role_doc["role_name"]==role_name:
                HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{role_name} already exists. Choose a different name.")
        permissions_list=role_req.permissions_list
        await isValidPermissions(permissions_list)
        permissions_list.extend(["read_msg", "write_msg", "delete_msg", "edit_msg"])
        update_doc={
            "$set": {
                "role_name": role_name,
                "permissions": permissions_list
            }
        }
        await DatabaseConnect.role_collection_update_one(role_id,update_doc)
        logger.info(f"Permission updated for role: {role_id} successfully in guild {guild_id}")
        return {
            "status": status.HTTP_202_ACCEPTED,
            "message": f"Role updated successfully"
        }
except Exception as e:
    logger.error(f"Failed to update role at '/guild_id/user_id/update-role' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't update role at the moment")

try:
    @router.get('/display-permissions', status_code=status.HTTP_200_OK)
    @limiter.limit("1/second")
    async def display_permissions(request: Request):
        permissions=[]
        for perm in Permission:
            permissions.append({perm.name: perm.value})
        logger.info("Permissions fetched successfully")
        logger.debug(f"Permissions: {permissions}")
        return {
            "status": status.HTTP_200_OK,
            "message": "Permissions fetched successfully",
            "Permissions": permissions
        }
except Exception as e:
    logger.error(f"Failed to display permissions at '/display-permissions' endpoint: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't display permissions at the moment")