from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.message import MessageStatusEnum, SysUserTypeEnum
from app.schemas.user import UserResponse
from app.schemas.activity import ActivityResponse


class SysUserBase(BaseModel):
    """系统用户基础模型"""
    name: str = Field(..., max_length=50, description="系统用户名称")
    introduction: str = Field(..., description="系统用户简介")
    user_type: SysUserTypeEnum = Field(default=SysUserTypeEnum.notification, description="用户类型")


class SysUserCreate(SysUserBase):
    """创建系统用户模型"""
    avatar: Optional[str] = Field(None, description="系统用户头像")


class SysUserUpdate(BaseModel):
    """更新系统用户模型"""
    name: Optional[str] = Field(None, max_length=50)
    introduction: Optional[str] = None
    user_type: Optional[SysUserTypeEnum] = None
    avatar: Optional[str] = None


class SysUserMenuBase(BaseModel):
    """系统用户菜单基础模型"""
    menu_name: str = Field(..., max_length=50, description="菜单名称")
    url: str = Field(..., max_length=255, description="小程序跳转路径")


class SysUserMenuCreate(SysUserMenuBase):
    """创建系统用户菜单模型"""
    sys_user_id: int = Field(..., description="系统用户ID")


class SysUserMenuResponse(SysUserMenuBase):
    """系统用户菜单响应模型"""
    id: int
    sys_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SysUserResponse(SysUserBase):
    """系统用户响应模型"""
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    
    # 关联数据
    menus: List[SysUserMenuResponse] = []

    class Config:
        from_attributes = True


class SysMessageBase(BaseModel):
    """系统消息基础模型"""
    title: str = Field(..., max_length=100, description="消息标题")
    content: str = Field(..., description="消息内容")


class SysMessageCreate(SysMessageBase):
    """创建系统消息模型"""
    sys_user_id: int = Field(..., description="系统用户ID")
    user_id: int = Field(..., description="接收用户ID")
    activity_id: Optional[int] = Field(None, description="关联活动ID")


class SysMessageBatchCreate(SysMessageBase):
    """批量创建系统消息模型"""
    sys_user_id: int = Field(..., description="系统用户ID")
    user_ids: List[int] = Field(..., description="接收用户ID列表")
    activity_id: Optional[int] = Field(None, description="关联活动ID")


class SysMessageUpdate(BaseModel):
    """更新系统消息模型"""
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    status: Optional[MessageStatusEnum] = None


class SysMessageResponse(SysMessageBase):
    """系统消息响应模型"""
    id: int
    sys_user_id: int
    user_id: int
    activity_id: Optional[int] = None
    status: MessageStatusEnum
    created_at: datetime
    read_at: Optional[datetime] = None
    
    # 关联数据
    sys_user: Optional[SysUserResponse] = None
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """消息列表响应模型"""
    items: List[SysMessageResponse]
    total: int
    unread_count: int
    page: int
    size: int


class MessageStatsResponse(BaseModel):
    """消息统计响应模型"""
    total_count: int = 0
    unread_count: int = 0
    today_count: int = 0
    
    class Config:
        from_attributes = True


class MarkMessageReadRequest(BaseModel):
    """标记消息已读请求模型"""
    message_ids: List[int] = Field(..., description="消息ID列表")


class MarkAllReadRequest(BaseModel):
    """标记全部已读请求模型"""
    user_id: Optional[int] = Field(None, description="用户ID，不传则为当前用户")