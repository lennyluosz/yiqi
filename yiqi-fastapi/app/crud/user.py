from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import UserProfile
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserProfile, UserCreate, UserUpdate]):
    def get_by_openid(self, db: Session, *, openid: str) -> Optional[UserProfile]:
        """根据微信openid获取用户"""
        return db.query(UserProfile).filter(UserProfile.openid == openid).first()

    def get_by_user_bh(self, db: Session, *, user_bh: str) -> Optional[UserProfile]:
        """根据用户编号获取用户"""
        return db.query(UserProfile).filter(UserProfile.user_bh == user_bh).first()

    def get_by_mobile(self, db: Session, *, mobile: str) -> Optional[UserProfile]:
        """根据手机号获取用户"""
        return db.query(UserProfile).filter(UserProfile.mobile == mobile).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[UserProfile]:
        """根据邮箱获取用户"""
        return db.query(UserProfile).filter(UserProfile.email == email).first()

    def search_users(
        self, 
        db: Session, 
        *, 
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserProfile]:
        """搜索用户"""
        return self.search(
            db,
            search_term=keyword,
            search_fields=["name", "nick_name", "mobile", "email"],
            skip=skip,
            limit=limit
        )

    def get_active_users(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserProfile]:
        """获取活跃用户"""
        return db.query(UserProfile).filter(
            UserProfile.is_active == True
        ).offset(skip).limit(limit).all()

    def create_user(self, db: Session, *, obj_in: UserCreate) -> UserProfile:
        """创建用户"""
        return self.create(db, obj_in=obj_in)

    def update_user(
        self,
        db: Session,
        *,
        db_obj: UserProfile,
        obj_in: UserUpdate
    ) -> UserProfile:
        """更新用户信息"""
        return self.update(db, db_obj=db_obj, obj_in=obj_in)

    def deactivate_user(self, db: Session, *, user_id: int) -> Optional[UserProfile]:
        """停用用户"""
        user = self.get(db, id=user_id)
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        return user

    def activate_user(self, db: Session, *, user_id: int) -> Optional[UserProfile]:
        """激活用户"""
        user = self.get(db, id=user_id)
        if user:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user


user_crud = CRUDUser(UserProfile)