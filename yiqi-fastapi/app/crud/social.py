from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, distinct
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.social import (
    ActivityUserInfo, SharingUser, CollectionUser, ReportUser, 
    BrowseUser, Comment, Feedback
)
from app.schemas.social import (
    ActivityUserInfoCreate, SharingUserCreate, CollectionUserCreate,
    ReportUserCreate, BrowseUserCreate, CommentCreate, CommentUpdate,
    FeedbackCreate, FeedbackUpdate
)


class CRUDActivityUserInfo(CRUDBase[ActivityUserInfo, ActivityUserInfoCreate, dict]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: ActivityUserInfoCreate, 
        user_id: int
    ) -> ActivityUserInfo:
        """创建报名记录"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = ActivityUserInfo(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_activity(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        activity_id: int
    ) -> Optional[ActivityUserInfo]:
        """检查用户是否已报名活动"""
        return db.query(ActivityUserInfo).filter(
            and_(
                ActivityUserInfo.user_id == user_id,
                ActivityUserInfo.activity_id == activity_id
            )
        ).first()

    def get_by_activity(
        self, 
        db: Session, 
        *, 
        activity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityUserInfo]:
        """获取活动的报名用户"""
        return db.query(ActivityUserInfo).options(
            joinedload(ActivityUserInfo.user)
        ).filter(
            ActivityUserInfo.activity_id == activity_id
        ).offset(skip).limit(limit).all()

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityUserInfo]:
        """获取用户报名的活动"""
        return db.query(ActivityUserInfo).options(
            joinedload(ActivityUserInfo.activity)
        ).filter(
            ActivityUserInfo.user_id == user_id
        ).order_by(desc(ActivityUserInfo.created_at)).offset(skip).limit(limit).all()

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动报名人数"""
        return db.query(ActivityUserInfo).filter(
            ActivityUserInfo.activity_id == activity_id
        ).count()

    def remove_registration(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        activity_id: int
    ) -> bool:
        """取消报名"""
        registration = self.get_by_user_activity(
            db, user_id=user_id, activity_id=activity_id
        )
        if registration:
            db.delete(registration)
            db.commit()
            return True
        return False


class CRUDSharingUser(CRUDBase[SharingUser, SharingUserCreate, dict]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: SharingUserCreate, 
        user_id: int
    ) -> SharingUser:
        """创建分享记录"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = SharingUser(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动分享次数"""
        return db.query(SharingUser).filter(
            SharingUser.activity_id == activity_id
        ).count()

    def get_recent_shares(
        self, 
        db: Session, 
        *, 
        user_id: int,
        days: int = 30,
        limit: int = 10
    ) -> List[SharingUser]:
        """获取用户最近分享"""
        since_date = datetime.now() - timedelta(days=days)
        
        return db.query(SharingUser).options(
            joinedload(SharingUser.activity)
        ).filter(
            and_(
                SharingUser.user_id == user_id,
                SharingUser.created_at >= since_date
            )
        ).order_by(desc(SharingUser.created_at)).limit(limit).all()


class CRUDCollectionUser(CRUDBase[CollectionUser, CollectionUserCreate, dict]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: CollectionUserCreate, 
        user_id: int
    ) -> CollectionUser:
        """创建收藏记录"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = CollectionUser(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_activity(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        activity_id: int
    ) -> Optional[CollectionUser]:
        """检查用户是否已收藏活动"""
        return db.query(CollectionUser).filter(
            and_(
                CollectionUser.user_id == user_id,
                CollectionUser.activity_id == activity_id
            )
        ).first()

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CollectionUser]:
        """获取用户收藏的活动"""
        return db.query(CollectionUser).options(
            joinedload(CollectionUser.activity)
        ).filter(
            CollectionUser.user_id == user_id
        ).order_by(desc(CollectionUser.created_at)).offset(skip).limit(limit).all()

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动收藏次数"""
        return db.query(CollectionUser).filter(
            CollectionUser.activity_id == activity_id
        ).count()

    def remove_collection(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        activity_id: int
    ) -> bool:
        """取消收藏"""
        collection = self.get_by_user_activity(
            db, user_id=user_id, activity_id=activity_id
        )
        if collection:
            db.delete(collection)
            db.commit()
            return True
        return False


class CRUDBrowseUser(CRUDBase[BrowseUser, BrowseUserCreate, dict]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: BrowseUserCreate, 
        user_id: int
    ) -> BrowseUser:
        """创建浏览记录"""
        # 检查是否已有当天的浏览记录，避免重复记录
        today = datetime.now().date()
        existing = db.query(BrowseUser).filter(
            and_(
                BrowseUser.user_id == user_id,
                BrowseUser.activity_id == obj_in.activity_id,
                func.date(BrowseUser.created_at) == today
            )
        ).first()
        
        if existing:
            return existing
            
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = BrowseUser(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动浏览次数"""
        return db.query(BrowseUser).filter(
            BrowseUser.activity_id == activity_id
        ).count()

    def count_unique_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动独立浏览用户数"""
        return db.query(distinct(BrowseUser.user_id)).filter(
            BrowseUser.activity_id == activity_id
        ).count()

    def get_user_history(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[BrowseUser]:
        """获取用户浏览历史"""
        return db.query(BrowseUser).options(
            joinedload(BrowseUser.activity)
        ).filter(
            BrowseUser.user_id == user_id
        ).order_by(desc(BrowseUser.created_at)).offset(skip).limit(limit).all()


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: CommentCreate, 
        user_id: int
    ) -> Comment:
        """创建评论"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = Comment(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_activity(
        self, 
        db: Session, 
        *, 
        activity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """获取活动的评论（只返回顶级评论）"""
        return db.query(Comment).options(
            joinedload(Comment.user),
            joinedload(Comment.replies)
        ).filter(
            and_(
                Comment.activity_id == activity_id,
                Comment.parent_comment_id.is_(None)
            )
        ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()

    def get_with_replies(self, db: Session, *, comment_id: int) -> Optional[Comment]:
        """获取评论及其所有回复"""
        return db.query(Comment).options(
            joinedload(Comment.user),
            joinedload(Comment.replies),
            joinedload(Comment.parent_comment)
        ).filter(Comment.id == comment_id).first()

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动评论数"""
        return db.query(Comment).filter(
            Comment.activity_id == activity_id
        ).count()

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """获取用户的评论"""
        return db.query(Comment).options(
            joinedload(Comment.activity)
        ).filter(
            Comment.user_id == user_id
        ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()


class CRUDReportUser(CRUDBase[ReportUser, ReportUserCreate, dict]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: ReportUserCreate, 
        user_id: int
    ) -> ReportUser:
        """创建举报记录"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = ReportUser(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_activity(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        activity_id: int
    ) -> Optional[ReportUser]:
        """检查用户是否已举报活动"""
        return db.query(ReportUser).filter(
            and_(
                ReportUser.user_id == user_id,
                ReportUser.activity_id == activity_id
            )
        ).first()

    def count_by_activity(self, db: Session, *, activity_id: int) -> int:
        """统计活动举报次数"""
        return db.query(ReportUser).filter(
            ReportUser.activity_id == activity_id
        ).count()

    def get_recent_reports(
        self, 
        db: Session, 
        *, 
        days: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReportUser]:
        """获取最近的举报记录"""
        since_date = datetime.now() - timedelta(days=days)
        
        return db.query(ReportUser).options(
            joinedload(ReportUser.user),
            joinedload(ReportUser.activity)
        ).filter(
            ReportUser.created_at >= since_date
        ).order_by(desc(ReportUser.created_at)).offset(skip).limit(limit).all()


class CRUDFeedback(CRUDBase[Feedback, FeedbackCreate, FeedbackUpdate]):
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: FeedbackCreate, 
        user_id: int
    ) -> Feedback:
        """创建反馈记录"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = Feedback(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """获取用户的反馈记录"""
        return db.query(Feedback).filter(
            Feedback.user_id == user_id
        ).order_by(desc(Feedback.created_at)).offset(skip).limit(limit).all()

    def get_unhandled(
        self, 
        db: Session, 
        *, 
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """获取未处理的反馈"""
        return db.query(Feedback).options(
            joinedload(Feedback.user)
        ).filter(
            Feedback.is_handled == False
        ).order_by(desc(Feedback.created_at)).offset(skip).limit(limit).all()

    def mark_handled(self, db: Session, *, feedback_id: int) -> Optional[Feedback]:
        """标记反馈为已处理"""
        feedback = self.get(db, id=feedback_id)
        if feedback:
            feedback.is_handled = True
            db.commit()
            db.refresh(feedback)
        return feedback


# 创建CRUD实例
activity_user_info_crud = CRUDActivityUserInfo(ActivityUserInfo)
sharing_user_crud = CRUDSharingUser(SharingUser)
collection_user_crud = CRUDCollectionUser(CollectionUser)
browse_user_crud = CRUDBrowseUser(BrowseUser)
comment_crud = CRUDComment(Comment)
report_user_crud = CRUDReportUser(ReportUser)
feedback_crud = CRUDFeedback(Feedback)