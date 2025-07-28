from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class GenderEnum(str, enum.Enum):
    male = "1"
    female = "2"


class UserProfile(Base):
    """用户模型"""
    __tablename__ = "users_userprofile"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(200), default="", comment="用户微信唯一ID")
    avatar_url = Column(String(500), default="", comment="用户微信头像")
    country = Column(String(100), default="", comment="用户微信国家")
    user_bh = Column(String(50), unique=True, comment="用户唯一ID")
    province = Column(String(100), default="", comment="用户微信省份")
    city = Column(String(100), default="", comment="用户微信城市")
    language = Column(String(100), default="", comment="用户微信语言")
    background = Column(String(255), comment="背景图")
    nick_name = Column(String(20), comment="微信用户名")
    name = Column(String(20), comment="用户名")
    birthday = Column(DateTime, comment="出生日期")
    avatar = Column(String(255), comment="用户头像")
    mobile = Column(String(11), comment="手机号")
    gender = Column(Enum(GenderEnum), default=GenderEnum.male, comment="性别")
    signature = Column(Text, default="世界为你转身，因为你肯冒险！", comment="用户签名")
    agreement = Column(Boolean, default=False, comment="是否阅读协议")
    email = Column(String(100), comment="邮箱")
    hashed_password = Column(String(128), nullable=True, comment="密码hash")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    created_at = Column(DateTime, server_default=func.now(), comment="注册时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name={self.name})>"