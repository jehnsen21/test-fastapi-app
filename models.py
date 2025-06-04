
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4

class ProjectStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class User(BaseModel):
    id: str = str(uuid4())
    username: str
    email: str
    password: str
    role: UserRole = UserRole.MEMBER
    created_at: datetime = datetime.utcnow()

class Project(BaseModel):
    id: str = str(uuid4())
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PENDING
    start_date: datetime = datetime.utcnow()
    end_date: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    owner_id: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.MEMBER

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.PENDING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    updated_at: datetime = datetime.utcnow()

class Token(BaseModel):
    access_token: str
    token_type: str