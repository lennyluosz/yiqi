from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.social import UserTypeEnum
from app.schemas.user import UserResponse
from app.schemas.activity import ActivityResponse


class ActivityUserInfoBase(BaseModel):
    """活动报名基础模型"""
    username: str = Field(..., max_length=20, description="真实姓名")
    wechat: str = Field(..., max_length=20, description="微信号")


class ActivityUserInfoCreate(ActivityUserInfoBase):
    """创建活动报名模型"""
    activity_id: int = Field(..., description="活动ID")
    user_type: UserTypeEnum = Field(default=UserTypeEnum.participant, description="用户类型")


class ActivityUserInfoResponse(ActivityUserInfoBase):
    """活动报名响应模型"""
    id: int
    user_id: int
    activity_id: int
    user_type: UserTypeEnum
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class SharingUserCreate(BaseModel):
    """创建分享记录模型"""
    activity_id: int = Field(..., description="分享活动ID")


class SharingUserResponse(BaseModel):
    """分享记录响应模型"""
    id: int
    user_id: int
    activity_id: int
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class CollectionUserCreate(BaseModel):
    """创建收藏记录模型"""
    activity_id: int = Field(..., description="收藏活动ID")


class CollectionUserResponse(BaseModel):
    """收藏记录响应模型"""
    id: int
    user_id: int
    activity_id: int
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class ReportUserCreate(BaseModel):
    """创建举报记录模型"""
    activity_id: int = Field(..., description="举报活动ID")
    reason: str = Field(..., max_length=500, description="举报理由")


class ReportUserResponse(BaseModel):
    """举报记录响应模型"""
    id: int
    user_id: int
    activity_id: int
    reason: str
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class BrowseUserCreate(BaseModel):
    """创建浏览记录模型"""
    activity_id: int = Field(..., description="浏览活动ID")


class BrowseUserResponse(BaseModel):
    """浏览记录响应模型"""
    id: int
    user_id: int
    activity_id: int
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., max_length=500, description="评论内容")


class CommentCreate(CommentBase):
    """创建评论模型"""
    activity_id: int = Field(..., description="评论活动ID")
    parent_comment_id: Optional[int] = Field(None, description="父评论ID")


class CommentUpdate(BaseModel):
    """更新评论模型"""
    content: Optional[str] = Field(None, max_length=500, description="评论内容")


class CommentResponse(CommentBase):
    """评论响应模型"""
    id: int
    user_id: int
    activity_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None
    activity: Optional[ActivityResponse] = None
    parent_comment: Optional['CommentResponse'] = None
    replies: List['CommentResponse'] = []

    class Config:
        from_attributes = True


class FeedbackBase(BaseModel):
    """反馈基础模型"""
    title: str = Field(..., max_length=100, description="反馈标题")
    content: str = Field(..., max_length=1000, description="反馈内容")


class FeedbackCreate(FeedbackBase):
    """创建反馈模型"""
    image: Optional[str] = Field(None, description="反馈图片")


class FeedbackUpdate(BaseModel):
    """更新反馈模型"""
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, max_length=1000)
    image: Optional[str] = None
    is_handled: Optional[bool] = None


class FeedbackResponse(FeedbackBase):
    """反馈响应模型"""
    id: int
    user_id: int
    image: Optional[str] = None
    is_handled: bool
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class SocialStatsResponse(BaseModel):
    """社交统计响应模型"""
    activity_id: int
    registration_count: int = 0
    collection_count: int = 0
    share_count: int = 0
    browse_count: int = 0
    comment_count: int = 0
    
    class Config:
        from_attributes = True


class UserSocialStatsResponse(BaseModel):
    """用户社交统计响应模型"""
    user_id: int
    created_activities: int = 0
    registered_activities: int = 0
    collected_activities: int = 0
    shared_activities: int = 0
    comments_count: int = 0
    
    class Config:
        from_attributes = True


# 更新CommentResponse的前向引用
CommentResponse.model_rebuild()