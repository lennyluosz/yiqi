from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserTypeEnum(str, enum.Enum):
    organizer = "0"  # 活动发起人
    participant = "1"  # 活动参加人


class ActivityUserInfo(Base):
    """活动报名信息模型"""
    __tablename__ = "useroperation_activityuserinfo"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="报名用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="活动ID")
    user_type = Column(Enum(UserTypeEnum), default=UserTypeEnum.participant, comment="用户类型")
    username = Column(String(20), comment="真实姓名")
    wechat = Column(String(20), comment="微信号")
    created_at = Column(DateTime, server_default=func.now(), comment="报名时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])


class SharingUser(Base):
    """用户分享记录模型"""
    __tablename__ = "useroperation_sharinguser"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="分享用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="分享活动ID")
    created_at = Column(DateTime, server_default=func.now(), comment="分享时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])


class CollectionUser(Base):
    """用户收藏记录模型"""
    __tablename__ = "useroperation_collectionuser"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="收藏用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="收藏活动ID")
    created_at = Column(DateTime, server_default=func.now(), comment="收藏时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])


class ReportUser(Base):
    """用户举报记录模型"""
    __tablename__ = "useroperation_reportuser"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="举报用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="举报活动ID")
    reason = Column(Text, comment="举报理由")
    created_at = Column(DateTime, server_default=func.now(), comment="举报时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])


class BrowseUser(Base):
    """用户浏览记录模型"""
    __tablename__ = "useroperation_browseuser"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="浏览用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="浏览活动ID")
    created_at = Column(DateTime, server_default=func.now(), comment="浏览时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])


class Comment(Base):
    """评论模型"""
    __tablename__ = "useroperation_comment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="评论用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), comment="评论活动ID")
    parent_comment_id = Column(Integer, ForeignKey("useroperation_comment.id"), nullable=True, comment="父评论ID")
    content = Column(Text, comment="评论内容")
    created_at = Column(DateTime, server_default=func.now(), comment="评论时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")


class Feedback(Base):
    """用户反馈模型"""
    __tablename__ = "useroperation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="反馈用户ID")
    title = Column(String(100), comment="反馈标题")
    content = Column(Text, comment="反馈内容")
    image = Column(String(255), nullable=True, comment="反馈图片")
    is_handled = Column(Boolean, default=False, comment="是否已处理")
    created_at = Column(DateTime, server_default=func.now(), comment="反馈时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("UserProfile", foreign_keys=[user_id])