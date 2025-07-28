from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MessageStatusEnum(str, enum.Enum):
    unread = "0"  # 未读
    read = "1"    # 已读


class SysUserTypeEnum(str, enum.Enum):
    notification = "0"  # 消息通知


class SysUser(Base):
    """系统用户模型"""
    __tablename__ = "messages_sysuser"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), comment="系统用户名称")
    introduction = Column(Text, comment="系统用户简介")
    user_type = Column(Enum(SysUserTypeEnum), default=SysUserTypeEnum.notification, comment="用户类型")
    avatar = Column(String(255), nullable=True, comment="系统用户头像")
    created_at = Column(DateTime, server_default=func.now(), comment="添加时间")

    # 关系
    menus = relationship("SysUserMenu", back_populates="sys_user", cascade="all, delete-orphan")
    messages = relationship("SysMessage", back_populates="sys_user")


class SysUserMenu(Base):
    """系统用户菜单模型"""
    __tablename__ = "messages_sysusermenu"

    id = Column(Integer, primary_key=True, index=True)
    sys_user_id = Column(Integer, ForeignKey("messages_sysuser.id"), comment="系统用户ID")
    menu_name = Column(String(50), comment="菜单名称")
    url = Column(String(255), comment="小程序跳转路径")
    created_at = Column(DateTime, server_default=func.now(), comment="添加时间")

    # 关系
    sys_user = relationship("SysUser", back_populates="menus")


class SysMessage(Base):
    """系统消息模型"""
    __tablename__ = "messages_sysmessage"

    id = Column(Integer, primary_key=True, index=True)
    sys_user_id = Column(Integer, ForeignKey("messages_sysuser.id"), comment="系统用户ID")
    user_id = Column(Integer, ForeignKey("users_userprofile.id"), comment="接收用户ID")
    activity_id = Column(Integer, ForeignKey("activity_activity.id"), nullable=True, comment="关联活动ID")
    title = Column(String(100), comment="消息标题")
    content = Column(Text, comment="消息内容")
    status = Column(Enum(MessageStatusEnum), default=MessageStatusEnum.unread, comment="阅读状态")
    created_at = Column(DateTime, server_default=func.now(), comment="消息时间")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")

    # 关系
    sys_user = relationship("SysUser", back_populates="messages")
    user = relationship("UserProfile", foreign_keys=[user_id])
    activity = relationship("Activity", foreign_keys=[activity_id])