from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import GenderEnum


class UserBase(BaseModel):
    """用户基础模型"""
    name: Optional[str] = None
    nick_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    gender: Optional[GenderEnum] = GenderEnum.male
    signature: Optional[str] = "世界为你转身，因为你肯冒险！"


class UserCreate(UserBase):
    """创建用户模型"""
    openid: str
    user_bh: str
    avatar_url: Optional[str] = ""
    country: Optional[str] = ""
    province: Optional[str] = ""
    city: Optional[str] = ""
    language: Optional[str] = ""
    agreement: bool = False


class UserUpdate(UserBase):
    """更新用户模型"""
    avatar: Optional[str] = None
    background: Optional[str] = None
    birthday: Optional[datetime] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    user_bh: str
    openid: str
    avatar_url: str
    avatar: Optional[str] = None
    background: Optional[str] = None
    country: str
    province: str
    city: str
    language: str
    birthday: Optional[datetime] = None
    agreement: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    items: List[UserResponse]
    total: int
    page: int
    size: int


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None