from pydantic import BaseModel
from typing import List

class RoleRequest(BaseModel):
    role_name: str
    permissions_list: List[str] = []
class AssignReq(BaseModel):
    role_id: str
    user_id: str