from pydantic import BaseModel, Field
from .models import Mine
from datetime import datetime

#POST METHODS
class ActCreate(BaseModel):
    title: str
    mine: Mine
    description: str
    requirement: str
    at: datetime = Field(example=datetime.now())

class ActUpdate(BaseModel):
    title: str
    mine: Mine
    description: str
    requirement: str
    at: datetime = Field(example=datetime.now())

class ActWhomCreate(BaseModel):
    act_id: int
    user_id: int

class ActFromCreate(BaseModel):
    act_id: int
    user_id: int

class ActItemsCreate(BaseModel):
    act_id: int
    content: str
    requirement: str
    note: str
    responsible_user: int
    deadline: datetime  = Field(example=datetime.now())


#GET METHODS
class ActUsers(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    position: str

class ActItems(BaseModel):
    id: int
    content: str
    requirement: str
    note: str
    responsible_user: ActUsers
    deadline: datetime  = Field(example=datetime.now())
    created_at: datetime
    updated_at: datetime

class ActReport(ActItems):
    status: str

class ActReportList(BaseModel):
    items: list[ActReport]
    total: int

class ActResp(BaseModel):
    id: int
    title: str
    mine: str
    description: str
    at: datetime  = Field(example=datetime.now())

class ActListResp(BaseModel):
    acts: list[ActResp]
    total: int

class ActDetails(BaseModel):
    id: int
    title: str
    mine: Mine
    description: str
    requirement: str
    at: datetime  = Field(example=datetime.now())
    whom: list[ActUsers]
    from_whom: list[ActUsers]
    items: list[ActItems]
    created_at: datetime
    updated_at: datetime




