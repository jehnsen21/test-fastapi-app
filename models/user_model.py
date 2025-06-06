from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from models.enums import UserRole

class User(BaseModel):
    id: str = str(uuid4())
    username: str
    email: str
    password: str
    role: UserRole = UserRole.MEMBER
    created_at: datetime = datetime.utcnow()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.MEMBER

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime