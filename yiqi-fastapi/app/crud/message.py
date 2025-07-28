from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from datetime import datetime, date, timedelta

from app.crud.base import CRUDBase
from app.models.message import SysUser, SysUserMenu, SysMessage
from app.schemas.message import (
    SysUserCreate, SysUserUpdate,
    SysUserMenuCreate,
    SysMessageCreate, SysMessageUpdate
)


class CRUDSysUser(CRUDBase[SysUser, SysUserCreate, SysUserUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[SysUser]:
        """根据名称获取系统用户"""
        return db.query(SysUser).filter(SysUser.name == name).first()

    def get_with_menus(self, db: Session, *, id: int) -> Optional[SysUser]:
        """获取系统用户及其菜单"""
        return db.query(SysUser).options(
            joinedload(SysUser.menus)
        ).filter(SysUser.id == id).first()


class CRUDSysUserMenu(CRUDBase[SysUserMenu, SysUserMenuCreate, dict]):
    def get_by_sys_user(self, db: Session, *, sys_user_id: int) -> List[SysUserMenu]:
        """获取系统用户的菜单列表"""
        return db.query(SysUserMenu).filter(
            SysUserMenu.sys_user_id == sys_user_id
        ).all()

    def create_with_sys_user(
        self, 
        db: Session, 
        *, 
        obj_in: SysUserMenuCreate
    ) -> SysUserMenu:
        """为系统用户创建菜单"""
        db_obj = SysUserMenu(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSysMessage(CRUDBase[SysMessage, SysMessageCreate, SysMessageUpdate]):
    def create_message(
        self, 
        db: Session, 
        *, 
        obj_in: SysMessageCreate
    ) -> SysMessage:
        """创建系统消息"""
        db_obj = SysMessage(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_batch_messages(
        self, 
        db: Session, 
        *, 
        sys_user_id: int,
        user_ids: List[int],
        title: str,
        content: str,
        activity_id: Optional[int] = None
    ) -> List[SysMessage]:
        """批量创建系统消息"""
        messages = []
        
        for user_id in user_ids:
            message_data = {
                "sys_user_id": sys_user_id,
                "user_id": user_id,
                "title": title,
                "content": content,
                "activity_id": activity_id
            }
            db_obj = SysMessage(**message_data)
            db.add(db_obj)
            messages.append(db_obj)
        
        db.commit()
        
        for message in messages:
            db.refresh(message)
        
        return messages

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[SysMessage]:
        """获取用户的消息"""
        query = db.query(SysMessage).options(
            joinedload(SysMessage.sys_user),
            joinedload(SysMessage.activity)
        ).filter(SysMessage.user_id == user_id)
        
        if unread_only:
            query = query.filter(SysMessage.status == "0")  # 未读
        
        return query.order_by(desc(SysMessage.created_at)).offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, *, id: int) -> Optional[SysMessage]:
        """获取消息详情，包含关联数据"""
        return db.query(SysMessage).options(
            joinedload(SysMessage.sys_user),
            joinedload(SysMessage.user),
            joinedload(SysMessage.activity)
        ).filter(SysMessage.id == id).first()

    def count_by_user(self, db: Session, *, user_id: int) -> int:
        """统计用户消息总数"""
        return db.query(SysMessage).filter(SysMessage.user_id == user_id).count()

    def count_unread_by_user(self, db: Session, *, user_id: int) -> int:
        """统计用户未读消息数"""
        return db.query(SysMessage).filter(
            and_(
                SysMessage.user_id == user_id,
                SysMessage.status == "0"  # 未读
            )
        ).count()

    def count_today_by_user(self, db: Session, *, user_id: int) -> int:
        """统计用户今日消息数"""
        today = date.today()
        return db.query(SysMessage).filter(
            and_(
                SysMessage.user_id == user_id,
                func.date(SysMessage.created_at) == today
            )
        ).count()

    def mark_as_read(self, db: Session, *, message_id: int) -> Optional[SysMessage]:
        """标记消息为已读"""
        message = self.get(db, id=message_id)
        if message and message.status == "0":  # 未读
            message.status = "1"  # 已读
            message.read_at = datetime.now()
            db.commit()
            db.refresh(message)
        return message

    def mark_messages_read(self, db: Session, *, message_ids: List[int]) -> int:
        """批量标记消息为已读"""
        count = db.query(SysMessage).filter(
            and_(
                SysMessage.id.in_(message_ids),
                SysMessage.status == "0"  # 只更新未读消息
            )
        ).update(
            {
                "status": "1",  # 已读
                "read_at": datetime.now()
            },
            synchronize_session=False
        )
        db.commit()
        return count

    def mark_all_read_by_user(self, db: Session, *, user_id: int) -> int:
        """标记用户所有消息为已读"""
        count = db.query(SysMessage).filter(
            and_(
                SysMessage.user_id == user_id,
                SysMessage.status == "0"  # 只更新未读消息
            )
        ).update(
            {
                "status": "1",  # 已读
                "read_at": datetime.now()
            },
            synchronize_session=False
        )
        db.commit()
        return count

    def delete_messages_batch(self, db: Session, *, message_ids: List[int]) -> int:
        """批量删除消息"""
        count = db.query(SysMessage).filter(
            SysMessage.id.in_(message_ids)
        ).count()
        
        db.query(SysMessage).filter(
            SysMessage.id.in_(message_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        return count

    def get_by_activity(
        self, 
        db: Session, 
        *, 
        activity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SysMessage]:
        """获取活动相关的消息"""
        return db.query(SysMessage).options(
            joinedload(SysMessage.sys_user),
            joinedload(SysMessage.user)
        ).filter(
            SysMessage.activity_id == activity_id
        ).order_by(desc(SysMessage.created_at)).offset(skip).limit(limit).all()

    def get_recent_messages(
        self, 
        db: Session, 
        *, 
        days: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[SysMessage]:
        """获取最近几天的消息"""
        since_date = datetime.now() - timedelta(days=days)
        
        return db.query(SysMessage).options(
            joinedload(SysMessage.sys_user),
            joinedload(SysMessage.user),
            joinedload(SysMessage.activity)
        ).filter(
            SysMessage.created_at >= since_date
        ).order_by(desc(SysMessage.created_at)).offset(skip).limit(limit).all()

    def cleanup_old_messages(
        self, 
        db: Session, 
        *, 
        days: int = 90
    ) -> int:
        """清理旧消息（超过指定天数的已读消息）"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = db.query(SysMessage).filter(
            and_(
                SysMessage.status == "1",  # 已读
                SysMessage.created_at < cutoff_date
            )
        ).count()
        
        db.query(SysMessage).filter(
            and_(
                SysMessage.status == "1",  # 已读
                SysMessage.created_at < cutoff_date
            )
        ).delete(synchronize_session=False)
        
        db.commit()
        return count


# 创建CRUD实例
sys_user_crud = CRUDSysUser(SysUser)
sys_user_menu_crud = CRUDSysUserMenu(SysUserMenu)
sys_message_crud = CRUDSysMessage(SysMessage)