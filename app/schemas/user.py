from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_admin: bool
    is_active: bool
    workspace_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserInvite(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "sales"  # admin | manager | sales


class UserRoleUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
