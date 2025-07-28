from pydantic import BaseModel
from typing import Optional
from app.models.user import GenderEnum


class WechatUserInfo(BaseModel):
    """微信用户信息"""
    nick_name: str
    avatar_url: str
    gender: GenderEnum
    country: str
    province: str
    city: str
    language: str


class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str
    user_info: WechatUserInfo