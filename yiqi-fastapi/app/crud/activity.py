from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import math

from app.crud.base import CRUDBase
from app.models.activity import Activity, ActivityType, ActivityImage, Slide
from app.models.social import ActivityUserInfo, CollectionUser, BrowseUser
from app.schemas.activity import (
    ActivityCreate, ActivityUpdate, ActivityTypeCreate, ActivityTypeUpdate,
    ActivityImageCreate, SlideCreate, SlideUpdate, ActivitySearchRequest
)


class CRUDActivityType(CRUDBase[ActivityType, ActivityTypeCreate, ActivityTypeUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ActivityType]:
        """根据名称获取活动类型"""
        return db.query(ActivityType).filter(ActivityType.name == name).first()

    def get_ordered_list(self, db: Session) -> List[ActivityType]:
        """获取按顺序排列的活动类型列表"""
        return db.query(ActivityType).order_by(ActivityType.index_num.asc()).all()


class CRUDActivity(CRUDBase[Activity, ActivityCreate, ActivityUpdate]):
    def create_with_user(self, db: Session, *, obj_in: ActivityCreate, user_id: int) -> Activity:
        """创建活动"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = Activity(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 创建发起人报名记录
        organizer_info = ActivityUserInfo(
            user_id=user_id,
            activity_id=db_obj.id,
            user_type="0",  # 发起人
            username=obj_in.username,
            wechat=obj_in.wechat
        )
        db.add(organizer_info)
        db.commit()
        
        return db_obj

    def get_with_details(self, db: Session, *, id: int) -> Optional[Activity]:
        """获取活动详情，包含关联数据"""
        return db.query(Activity).options(
            joinedload(Activity.activity_type),
            joinedload(Activity.images),
            joinedload(Activity.user)
        ).filter(Activity.id == id).first()

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_draft: bool = False
    ) -> List[Activity]:
        """获取用户创建的活动"""
        query = db.query(Activity).filter(Activity.user_id == user_id)
        
        if not include_draft:
            query = query.filter(Activity.is_draft == False)
            
        return query.options(
            joinedload(Activity.activity_type)
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()

    def search_activities(
        self,
        db: Session,
        *,
        search_params: ActivitySearchRequest,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """搜索活动"""
        query = db.query(Activity).filter(
            Activity.is_draft == False,
            Activity.audit == "1"  # 已审核
        )

        # 关键词搜索
        if search_params.keyword:
            query = query.filter(
                or_(
                    Activity.title.like(f"%{search_params.keyword}%"),
                    Activity.content.like(f"%{search_params.keyword}%"),
                    Activity.address.like(f"%{search_params.keyword}%")
                )
            )

        # 活动类型筛选
        if search_params.activity_type_id:
            query = query.filter(Activity.activity_type_id == search_params.activity_type_id)

        # 城市筛选
        if search_params.city:
            query = query.filter(Activity.address.like(f"%{search_params.city}%"))

        # 时间范围筛选
        if search_params.start_date:
            query = query.filter(Activity.start_date >= search_params.start_date)
        if search_params.end_date:
            query = query.filter(Activity.end_date <= search_params.end_date)

        # 地理位置筛选（简单的矩形范围筛选）
        if search_params.latitude and search_params.longitude and search_params.radius:
            lat_range = search_params.radius / 111.0  # 1度约等于111公里
            lng_range = search_params.radius / (111.0 * math.cos(math.radians(search_params.latitude)))
            
            query = query.filter(
                and_(
                    Activity.latitude.between(
                        str(search_params.latitude - lat_range),
                        str(search_params.latitude + lat_range)
                    ),
                    Activity.longitude.between(
                        str(search_params.longitude - lng_range),
                        str(search_params.longitude + lng_range)
                    )
                )
            )

        return query.options(
            joinedload(Activity.activity_type)
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()

    def get_popular_activities(
        self,
        db: Session,
        *,
        days: int = 7,
        limit: int = 10
    ) -> List[Activity]:
        """获取热门活动（按报名人数排序）"""
        since_date = datetime.now() - timedelta(days=days)
        
        return db.query(Activity).filter(
            Activity.is_draft == False,
            Activity.audit == "1",
            Activity.created_at >= since_date
        ).order_by(desc(Activity.registration_number)).limit(limit).all()

    def get_upcoming_activities(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """获取即将开始的活动"""
        now = datetime.now()
        
        return db.query(Activity).filter(
            Activity.is_draft == False,
            Activity.audit == "1",
            Activity.start_date > now
        ).options(
            joinedload(Activity.activity_type)
        ).order_by(asc(Activity.start_date)).offset(skip).limit(limit).all()

    def increment_registration(self, db: Session, *, activity_id: int) -> Optional[Activity]:
        """增加报名人数"""
        activity = self.get(db, id=activity_id)
        if activity:
            activity.registration_number += 1
            db.commit()
            db.refresh(activity)
        return activity

    def decrement_registration(self, db: Session, *, activity_id: int) -> Optional[Activity]:
        """减少报名人数"""
        activity = self.get(db, id=activity_id)
        if activity and activity.registration_number > 0:
            activity.registration_number -= 1
            db.commit()
            db.refresh(activity)
        return activity

    def update_audit_status(self, db: Session, *, activity_id: int, audit_status: str) -> Optional[Activity]:
        """更新审核状态"""
        activity = self.get(db, id=activity_id)
        if activity:
            activity.audit = audit_status
            db.commit()
            db.refresh(activity)
        return activity


class CRUDActivityImage(CRUDBase[ActivityImage, ActivityImageCreate, dict]):
    def create_with_activity(
        self, 
        db: Session, 
        *, 
        obj_in: ActivityImageCreate, 
        activity_id: int
    ) -> ActivityImage:
        """为活动创建图片"""
        obj_in_data = obj_in.dict()
        obj_in_data["activity_id"] = activity_id
        db_obj = ActivityImage(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_activity(self, db: Session, *, activity_id: int) -> List[ActivityImage]:
        """获取活动的所有图片"""
        return db.query(ActivityImage).filter(
            ActivityImage.activity_id == activity_id
        ).order_by(ActivityImage.index_num.asc()).all()

    def delete_by_activity(self, db: Session, *, activity_id: int) -> int:
        """删除活动的所有图片"""
        count = db.query(ActivityImage).filter(ActivityImage.activity_id == activity_id).count()
        db.query(ActivityImage).filter(ActivityImage.activity_id == activity_id).delete()
        db.commit()
        return count


class CRUDSlide(CRUDBase[Slide, SlideCreate, SlideUpdate]):
    def get_ordered_list(self, db: Session) -> List[Slide]:
        """获取按顺序排列的轮播图列表"""
        return db.query(Slide).options(
            joinedload(Slide.activity)
        ).order_by(Slide.index_num.asc()).all()

    def get_active_slides(self, db: Session, *, limit: int = 5) -> List[Slide]:
        """获取活跃的轮播图（关联的活动未过期）"""
        now = datetime.now()
        
        return db.query(Slide).join(Activity).filter(
            Activity.end_date > now,
            Activity.is_draft == False,
            Activity.audit == "1"
        ).options(
            joinedload(Slide.activity)
        ).order_by(Slide.index_num.asc()).limit(limit).all()


# 创建CRUD实例
activity_type_crud = CRUDActivityType(ActivityType)
activity_crud = CRUDActivity(Activity)
activity_image_crud = CRUDActivityImage(ActivityImage)
slide_crud = CRUDSlide(Slide)