from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserProfile
from app.crud.activity import activity_crud
from app.crud.social import (
    activity_user_info_crud, sharing_user_crud, collection_user_crud,
    browse_user_crud, comment_crud, report_user_crud, feedback_crud
)
from app.schemas.social import (
    ActivityUserInfoCreate, ActivityUserInfoResponse,
    SharingUserCreate, SharingUserResponse,
    CollectionUserCreate, CollectionUserResponse,
    BrowseUserCreate, BrowseUserResponse,
    CommentCreate, CommentUpdate, CommentResponse,
    ReportUserCreate, ReportUserResponse,
    FeedbackCreate, FeedbackUpdate, FeedbackResponse,
    SocialStatsResponse, UserSocialStatsResponse
)

router = APIRouter()


# 活动报名相关
@router.post("/register", response_model=ActivityUserInfoResponse)
async def register_activity(
    registration_in: ActivityUserInfoCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """报名活动"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=registration_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查是否已报名
    existing_registration = activity_user_info_crud.get_by_user_activity(
        db, user_id=current_user.id, activity_id=registration_in.activity_id
    )
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已报名此活动"
        )
    
    # 检查活动是否已满员
    if activity.registration_number >= activity.limit_num:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="活动报名已满"
        )
    
    # 创建报名记录
    registration = activity_user_info_crud.create_with_user(
        db, obj_in=registration_in, user_id=current_user.id
    )
    
    # 更新活动报名人数
    activity_crud.increment_registration(db, activity_id=registration_in.activity_id)
    
    return registration


@router.delete("/register/{activity_id}")
async def cancel_registration(
    activity_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消报名"""
    success = activity_user_info_crud.remove_registration(
        db, user_id=current_user.id, activity_id=activity_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到报名记录"
        )
    
    # 更新活动报名人数
    activity_crud.decrement_registration(db, activity_id=activity_id)
    
    return {"message": "取消报名成功"}


@router.get("/registrations/{activity_id}", response_model=List[ActivityUserInfoResponse])
async def get_activity_registrations(
    activity_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """获取活动报名列表"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return activity_user_info_crud.get_by_activity(
        db, activity_id=activity_id, skip=skip, limit=limit
    )


@router.get("/my-registrations", response_model=List[ActivityUserInfoResponse])
async def get_my_registrations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的报名记录"""
    return activity_user_info_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


# 收藏相关
@router.post("/collect", response_model=CollectionUserResponse)
async def collect_activity(
    collection_in: CollectionUserCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """收藏活动"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=collection_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查是否已收藏
    existing_collection = collection_user_crud.get_by_user_activity(
        db, user_id=current_user.id, activity_id=collection_in.activity_id
    )
    if existing_collection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已收藏此活动"
        )
    
    return collection_user_crud.create_with_user(
        db, obj_in=collection_in, user_id=current_user.id
    )


@router.delete("/collect/{activity_id}")
async def uncollect_activity(
    activity_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    success = collection_user_crud.remove_collection(
        db, user_id=current_user.id, activity_id=activity_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到收藏记录"
        )
    
    return {"message": "取消收藏成功"}


@router.get("/my-collections", response_model=List[CollectionUserResponse])
async def get_my_collections(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的收藏"""
    return collection_user_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


# 分享相关
@router.post("/share", response_model=SharingUserResponse)
async def share_activity(
    share_in: SharingUserCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分享活动"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=share_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return sharing_user_crud.create_with_user(
        db, obj_in=share_in, user_id=current_user.id
    )


@router.get("/my-shares", response_model=List[SharingUserResponse])
async def get_my_shares(
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的分享记录"""
    return sharing_user_crud.get_recent_shares(
        db, user_id=current_user.id, days=days, limit=limit
    )


# 浏览记录
@router.post("/browse", response_model=BrowseUserResponse)
async def record_browse(
    browse_in: BrowseUserCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """记录浏览"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=browse_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return browse_user_crud.create_with_user(
        db, obj_in=browse_in, user_id=current_user.id
    )


@router.get("/my-browse-history", response_model=List[BrowseUserResponse])
async def get_my_browse_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的浏览历史"""
    return browse_user_crud.get_user_history(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


# 评论相关
@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment_in: CommentCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建评论"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=comment_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 如果是回复评论，检查父评论是否存在
    if comment_in.parent_comment_id:
        parent_comment = comment_crud.get(db, id=comment_in.parent_comment_id)
        if not parent_comment or parent_comment.activity_id != comment_in.activity_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )
    
    return comment_crud.create_with_user(
        db, obj_in=comment_in, user_id=current_user.id
    )


@router.get("/comments/{activity_id}", response_model=List[CommentResponse])
async def get_activity_comments(
    activity_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """获取活动评论"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return comment_crud.get_by_activity(
        db, activity_id=activity_id, skip=skip, limit=limit
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新评论"""
    comment = comment_crud.get(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限：只有评论作者可以修改
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此评论"
        )
    
    return comment_crud.update(db, db_obj=comment, obj_in=comment_in)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除评论"""
    comment = comment_crud.get(db, id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限：只有评论作者可以删除
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此评论"
        )
    
    comment_crud.remove(db, id=comment_id)
    return {"message": "评论已删除"}


@router.get("/my-comments", response_model=List[CommentResponse])
async def get_my_comments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的评论"""
    return comment_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


# 举报相关
@router.post("/report", response_model=ReportUserResponse)
async def report_activity(
    report_in: ReportUserCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """举报活动"""
    # 检查活动是否存在
    activity = activity_crud.get(db, id=report_in.activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查是否已举报
    existing_report = report_user_crud.get_by_user_activity(
        db, user_id=current_user.id, activity_id=report_in.activity_id
    )
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已举报过此活动"
        )
    
    return report_user_crud.create_with_user(
        db, obj_in=report_in, user_id=current_user.id
    )


# 反馈相关
@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback_in: FeedbackCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建反馈"""
    return feedback_crud.create_with_user(
        db, obj_in=feedback_in, user_id=current_user.id
    )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的反馈"""
    return feedback_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


# 统计相关
@router.get("/stats/{activity_id}", response_model=SocialStatsResponse)
async def get_activity_stats(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """获取活动社交统计"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return SocialStatsResponse(
        activity_id=activity_id,
        registration_count=activity_user_info_crud.count_by_activity(db, activity_id=activity_id),
        collection_count=collection_user_crud.count_by_activity(db, activity_id=activity_id),
        share_count=sharing_user_crud.count_by_activity(db, activity_id=activity_id),
        browse_count=browse_user_crud.count_by_activity(db, activity_id=activity_id),
        comment_count=comment_crud.count_by_activity(db, activity_id=activity_id)
    )


@router.get("/my-stats", response_model=UserSocialStatsResponse)
async def get_my_social_stats(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我的社交统计"""
    # 这里使用简单的查询统计，实际项目中可以考虑缓存
    created_activities = activity_crud.count(db)  # 需要添加按用户统计的方法
    registered_activities = len(activity_user_info_crud.get_by_user(db, user_id=current_user.id, limit=1000))
    collected_activities = len(collection_user_crud.get_by_user(db, user_id=current_user.id, limit=1000))
    shared_activities = len(sharing_user_crud.get_recent_shares(db, user_id=current_user.id, days=365, limit=1000))
    comments_count = len(comment_crud.get_by_user(db, user_id=current_user.id, limit=1000))
    
    return UserSocialStatsResponse(
        user_id=current_user.id,
        created_activities=created_activities,
        registered_activities=registered_activities,
        collected_activities=collected_activities,
        shared_activities=shared_activities,
        comments_count=comments_count
    )