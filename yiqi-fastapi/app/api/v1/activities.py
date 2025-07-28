from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserProfile
from app.crud.activity import activity_crud, activity_type_crud, activity_image_crud, slide_crud
from app.schemas.activity import (
    ActivityCreate, ActivityUpdate, ActivityResponse, ActivityListResponse,
    ActivityTypeResponse, ActivitySearchRequest, SlideResponse,
    ActivityImageCreate, ActivityImageResponse
)

router = APIRouter()


@router.get("/types", response_model=List[ActivityTypeResponse])
async def get_activity_types(db: Session = Depends(get_db)):
    """获取活动类型列表"""
    return activity_type_crud.get_ordered_list(db)


@router.get("/slides", response_model=List[SlideResponse])
async def get_slides(
    limit: int = Query(default=5, le=10),
    db: Session = Depends(get_db)
):
    """获取轮播图列表"""
    return slide_crud.get_active_slides(db, limit=limit)


@router.get("/", response_model=ActivityListResponse)
async def get_activities(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """获取活动列表"""
    activities = activity_crud.get_multi(
        db, skip=skip, limit=limit, order_by="created_at", desc_order=True
    )
    total = activity_crud.count(db)
    
    return ActivityListResponse(
        items=activities,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.post("/search", response_model=ActivityListResponse)
async def search_activities(
    search_params: ActivitySearchRequest,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """搜索活动"""
    activities = activity_crud.search_activities(
        db, search_params=search_params, skip=skip, limit=limit
    )
    
    # 简单的总数估算（为了性能考虑）
    total = len(activities) if len(activities) < limit else (skip + len(activities) + 1)
    
    return ActivityListResponse(
        items=activities,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/popular", response_model=List[ActivityResponse])
async def get_popular_activities(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """获取热门活动"""
    return activity_crud.get_popular_activities(db, days=days, limit=limit)


@router.get("/upcoming", response_model=ActivityListResponse)
async def get_upcoming_activities(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """获取即将开始的活动"""
    activities = activity_crud.get_upcoming_activities(db, skip=skip, limit=limit)
    total = len(activities) if len(activities) < limit else (skip + len(activities) + 1)
    
    return ActivityListResponse(
        items=activities,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_in: ActivityCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建活动"""
    # 验证活动类型是否存在
    activity_type = activity_type_crud.get(db, id=activity_in.activity_type_id)
    if not activity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动类型不存在"
        )
    
    return activity_crud.create_with_user(db, obj_in=activity_in, user_id=current_user.id)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """获取活动详情"""
    activity = activity_crud.get_with_details(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_in: ActivityUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新活动"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限：只有活动创建者可以修改
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此活动"
        )
    
    return activity_crud.update(db, db_obj=activity, obj_in=activity_in)


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除活动"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限：只有活动创建者可以删除
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此活动"
        )
    
    activity_crud.remove(db, id=activity_id)
    return {"message": "活动已删除"}


@router.post("/{activity_id}/images", response_model=ActivityImageResponse)
async def add_activity_image(
    activity_id: int,
    image_in: ActivityImageCreate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """为活动添加图片"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限：只有活动创建者可以添加图片
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此活动添加图片"
        )
    
    return activity_image_crud.create_with_activity(
        db, obj_in=image_in, activity_id=activity_id
    )


@router.get("/{activity_id}/images", response_model=List[ActivityImageResponse])
async def get_activity_images(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """获取活动图片列表"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    return activity_image_crud.get_by_activity(db, activity_id=activity_id)


@router.delete("/{activity_id}/images/{image_id}")
async def delete_activity_image(
    activity_id: int,
    image_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除活动图片"""
    activity = activity_crud.get(db, id=activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="活动不存在"
        )
    
    # 检查权限：只有活动创建者可以删除图片
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此活动的图片"
        )
    
    image = activity_image_crud.get(db, id=image_id)
    if not image or image.activity_id != activity_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在"
        )
    
    activity_image_crud.remove(db, id=image_id)
    return {"message": "图片已删除"}


@router.get("/user/my-activities", response_model=ActivityListResponse)
async def get_my_activities(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    include_draft: bool = Query(default=False),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我创建的活动"""
    activities = activity_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit, include_draft=include_draft
    )
    
    total = len(activities) if len(activities) < limit else (skip + len(activities) + 1)
    
    return ActivityListResponse(
        items=activities,
        total=total,
        page=skip // limit + 1,
        size=limit
    )