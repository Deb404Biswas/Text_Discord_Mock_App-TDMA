from app.services.database.database import db_service
from app.core.config.config import settings
async def default_roles_setup():
    if not await db_service.role_find_one(settings.OWNER_ROLE_ID):
        owner_role_doc={
            "_id":settings.OWNER_ROLE_ID,
            "role_name":"guild-owner",
            "permissions":['guild_owner']
        }
        await db_service.role_insert_one(owner_role_doc)
    if not await db_service.role_find_one(settings.MEMBER_ROLE_ID):
        member_role_doc={
            "_id":settings.MEMBER_ROLE_ID,
            "role_name":"member",
            "permissions":["read_msg","write_msg","delete_msg","edit_msg"]
        }
        await db_service.role_insert_one(member_role_doc)