#!/usr/bin/env python3
"""
创建管理员用户的脚本
"""
import asyncio
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import SessionLocal, engine
from app.models.user import UserProfile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员
        admin = db.query(UserProfile).filter(UserProfile.is_admin == True).first()
        if admin:
            print(f"管理员用户已存在: {admin.name} ({admin.mobile})")
            return
        
        # 创建管理员用户
        hashed_password = pwd_context.hash("admin123456")  # 默认密码
        
        admin_user = UserProfile(
            name="管理员",
            nick_name="系统管理员",
            mobile="admin",  # 登录用户名
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True,
            user_bh="admin_001",
            signature="系统管理员账户"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"管理员用户创建成功!")
        print(f"用户名: admin")
        print(f"密码: admin123456")
        print(f"请及时修改默认密码!")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()