from pydantic import BaseModel

class GroupCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    group_id: int

class AvailabilityCreate(BaseModel):
    user_id: int
    availability: str
