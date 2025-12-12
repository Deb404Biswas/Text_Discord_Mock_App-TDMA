from app.services.database.database import DatabaseConnect
from app.core.config.config import settings
async def default_roles_setup():
    owner_role={
        "_id":settings.OWNER_ROLE_ID,
        "role_name":"guild-owner",
        "users":[],
        "permissions":['guild_owner']
    }
    await DatabaseConnect.role_collection_insert_one(owner_role)
    member_role={
        "_id":settings.MEMBER_ROLE_ID,
        "role_name":"member",
        "users":[],
        "permissions":['read_msg','write_msg']
    }
    await DatabaseConnect.role_collection_insert_one(member_role)