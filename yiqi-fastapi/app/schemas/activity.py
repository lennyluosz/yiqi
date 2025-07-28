from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.activity import AuditEnum


class ActivityTypeBase(BaseModel):
    """活动类型基础模型"""
    name: str = Field(..., max_length=50, description="类别名称")
    introduction: str = Field(..., max_length=300, description="类别简介")
    index_num: int = Field(default=0, description="排列顺序")


class ActivityTypeCreate(ActivityTypeBase):
    """创建活动类型模型"""
    cover_image: Optional[str] = None


class ActivityTypeUpdate(ActivityTypeBase):
    """更新活动类型模型"""
    name: Optional[str] = None
    introduction: Optional[str] = None
    cover_image: Optional[str] = None


class ActivityTypeResponse(ActivityTypeBase):
    """活动类型响应模型"""
    id: int
    cover_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityImageBase(BaseModel):
    """活动图片基础模型"""
    image: str = Field(..., description="图片路径")
    index_num: int = Field(default=0, description="图片顺序")


class ActivityImageCreate(ActivityImageBase):
    """创建活动图片模型"""
    pass


class ActivityImageResponse(ActivityImageBase):
    """活动图片响应模型"""
    id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    """活动基础模型"""
    title: str = Field(..., max_length=50, description="活动标题")
    content: str = Field(..., max_length=1000, description="活动内容")
    start_date: datetime = Field(..., description="开始时间")
    end_date: datetime = Field(..., description="结束时间")
    address: str = Field(..., max_length=255, description="活动地点")
    latitude: str = Field(..., max_length=200, description="纬度")
    longitude: str = Field(..., max_length=200, description="经度")
    limit_num: int = Field(default=10, ge=1, le=1000, description="限制人数")
    username: str = Field(..., max_length=20, description="联系人姓名")
    wechat: str = Field(..., max_length=20, description="微信号")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class ActivityCreate(ActivityBase):
    """创建活动模型"""
    activity_type_id: int = Field(..., description="活动类别ID")
    cover_image: Optional[str] = None
    group_code: Optional[str] = None
    is_agree: bool = Field(default=True, description="是否同意协议")
    is_draft: bool = Field(default=False, description="是否草稿")


class ActivityUpdate(BaseModel):
    """更新活动模型"""
    title: Optional[str] = Field(None, max_length=50)
    content: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[str] = Field(None, max_length=200)
    longitude: Optional[str] = Field(None, max_length=200)
    limit_num: Optional[int] = Field(None, ge=1, le=1000)
    username: Optional[str] = Field(None, max_length=20)
    wechat: Optional[str] = Field(None, max_length=20)
    cover_image: Optional[str] = None
    group_code: Optional[str] = None
    is_draft: Optional[bool] = None


class ActivityResponse(ActivityBase):
    """活动响应模型"""
    id: int
    user_id: int
    activity_type_id: int
    cover_image: Optional[str] = None
    registration_number: int
    group_code: Optional[str] = None
    is_agree: bool
    is_draft: bool
    audit: AuditEnum
    created_at: datetime
    updated_at: datetime
    
    # 关联数据
    activity_type: Optional[ActivityTypeResponse] = None
    images: List[ActivityImageResponse] = []

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """活动列表响应模型"""
    items: List[ActivityResponse]
    total: int
    page: int
    size: int


class ActivitySearchRequest(BaseModel):
    """活动搜索请求模型"""
    keyword: Optional[str] = None
    activity_type_id: Optional[int] = None
    city: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = Field(default=10.0, ge=0.1, le=100.0, description="搜索半径(公里)")


class SlideBase(BaseModel):
    """轮播图基础模型"""
    activity_id: int = Field(..., description="关联活动ID")
    image: str = Field(..., description="轮播图片")
    index_num: int = Field(default=0, description="显示顺序")


class SlideCreate(SlideBase):
    """创建轮播图模型"""
    pass


class SlideUpdate(BaseModel):
    """更新轮播图模型"""
    activity_id: Optional[int] = None
    image: Optional[str] = None
    index_num: Optional[int] = None


class SlideResponse(SlideBase):
    """轮播图响应模型"""
    id: int
    created_at: datetime
    activity: Optional[ActivityResponse] = None

    class Config:
        from_attributes = True