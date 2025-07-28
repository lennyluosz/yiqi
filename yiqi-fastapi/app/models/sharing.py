from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class SharingPageEnum(str, enum.Enum):
    general = "0"    # 通用页面
    activity = "1"   # 活动页面
    publish = "2"    # 发布页面
    discover = "3"   # 发现页面
    message = "4"    # 消息页面
    content = "5"    # 内容页面


class SharingSet(Base):
    """分享设置模型"""
    __tablename__ = "sharing_sharingset"

    id = Column(Integer, primary_key=True, index=True)
    page_type = Column(Enum(SharingPageEnum), default=SharingPageEnum.general, comment="分享页面类型")
    title = Column(String(100), comment="分享标题")
    image_url = Column(String(255), nullable=True, comment="分享图片")
    created_at = Column(DateTime, server_default=func.now(), comment="添加时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<SharingSet(id={self.id}, page_type={self.page_type}, title={self.title})>"