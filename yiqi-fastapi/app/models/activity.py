from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class AuditEnum(str, enum.Enum):
    pending = "0"
    approved = "1"


class ActivityType(Base):
    """活动类别模型"""
    __tablename__ = "activity_activitytype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), comment="类别名称")
    cover_image = Column(String(255), comment="类别图片")
    introduction = Column(Text, comment="类别简介")
    index_num = Column(Integer, default=0, comment="排列顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="添加时间")

    # 关系
    activities = relationship("Activity", back_populates="activity_type")


class Activity(Base):
    """活动模型"""
    __tablename__ = "activity_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="发布用户ID")
    cover_image = Column(String(255), comment="封面图片")
    title = Column(String(50), comment="活动标题")
    content = Column(Text, comment="活动内容")
    start_date = Column(DateTime, comment="开始时间")
    end_date = Column(DateTime, comment="结束时间")
    address = Column(String(255), comment="活动地点")
    latitude = Column(String(200), comment="纬度")
    longitude = Column(String(200), comment="经度")
    registration_number = Column(Integer, default=0, comment="报名人数")
    activity_type_id = Column(Integer, ForeignKey("activity_activitytype.id"), comment="活动类别ID")
    limit_num = Column(Integer, default=10, comment="限制人数")
    username = Column(String(20), comment="联系人姓名")
    wechat = Column(String(20), comment="微信号")
    group_code = Column(String(255), comment="群二维码")
    is_agree = Column(Boolean, default=False, comment="是否同意协议")
    is_draft = Column(Boolean, default=False, comment="是否草稿")
    audit = Column(Enum(AuditEnum), default=AuditEnum.pending, comment="审核状态")
    created_at = Column(DateTime, server_default=func.now(), comment="发布时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    activity_type = relationship("ActivityType", back_populates="activities")
    images = relationship("ActivityImage", back_populates="activity", cascade="all, delete-orphan")
    user = relationship("UserProfile", foreign_keys=[user_id])
    
    # 社交关系
    registrations = relationship("ActivityUserInfo", foreign_keys="ActivityUserInfo.activity_id", cascade="all, delete-orphan")
    collections = relationship("CollectionUser", foreign_keys="CollectionUser.activity_id", cascade="all, delete-orphan")
    shares = relationship("SharingUser", foreign_keys="SharingUser.activity_id", cascade="all, delete-orphan")
    browses = relationship("BrowseUser", foreign_keys="BrowseUser.activity_id", cascade="all, delete-orphan")
    comments = relationship("Comment", foreign_keys="Comment.activity_id", cascade="all, delete-orphan")
    reports = relationship("ReportUser", foreign_keys="ReportUser.activity_id", cascade="all, delete-orphan")


class ActivityImage(Base):
    """活动图片模型"""
    __tablename__ = "activity_activityimage"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="活动ID")
    image = Column(String(255), comment="图片路径")
    index_num = Column(Integer, default=0, comment="图片顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")

    # 关系
    activity = relationship("Activity", back_populates="images")


class Slide(Base):
    """首页轮播图模型"""
    __tablename__ = "activity_slide"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="关联活动ID")
    image = Column(String(255), comment="轮播图片")
    index_num = Column(Integer, default=0, comment="显示顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="添加时间")