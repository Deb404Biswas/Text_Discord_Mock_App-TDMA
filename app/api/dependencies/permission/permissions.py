from enum import Enum

class Permission(str, Enum):
    read_msg="read messages from channel"
    write_msg="write messages to channel"
    delete_msg="delete messages from channel"
    edit_msg="edit messages in channel"
    kick_member="kick member from guild"
    add_member="add member to guild"
    mod_guild="modify guild name,channel name"
    guild_owner="all permissions in guild"
    manage_roles="create,assign,update roles in guild"
    create_channel="create channels in guild"
    del_channel="Delete a channel in guild"