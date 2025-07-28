from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserProfile
from app.crud.message import sys_message_crud, sys_user_crud
from app.schemas.message import (
    SysMessageResponse, MessageListResponse, MessageStatsResponse,
    MarkMessageReadRequest, MarkAllReadRequest
)

router = APIRouter()


@router.get("/", response_model=MessageListResponse)
async def get_messages(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    unread_only: bool = Query(default=False),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取消息列表"""
    messages = sys_message_crud.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit, unread_only=unread_only
    )
    
    total = sys_message_crud.count_by_user(db, user_id=current_user.id)
    unread_count = sys_message_crud.count_unread_by_user(db, user_id=current_user.id)
    
    return MessageListResponse(
        items=messages,
        total=total,
        unread_count=unread_count,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{message_id}", response_model=SysMessageResponse)
async def get_message(
    message_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取消息详情"""
    message = sys_message_crud.get_with_details(db, id=message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 检查权限：只能查看自己的消息
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此消息"
        )
    
    # 自动标记为已读
    if message.status == "0":  # 未读
        sys_message_crud.mark_as_read(db, message_id=message_id)
    
    return message


@router.post("/mark-read")
async def mark_messages_read(
    request: MarkMessageReadRequest,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    # 验证消息是否属于当前用户
    for message_id in request.message_ids:
        message = sys_message_crud.get(db, id=message_id)
        if not message or message.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"消息 {message_id} 不存在或无权访问"
            )
    
    # 批量标记为已读
    count = sys_message_crud.mark_messages_read(db, message_ids=request.message_ids)
    
    return {"message": f"已标记 {count} 条消息为已读"}


@router.post("/mark-all-read")
async def mark_all_messages_read(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """标记所有消息为已读"""
    count = sys_message_crud.mark_all_read_by_user(db, user_id=current_user.id)
    
    return {"message": f"已标记 {count} 条消息为已读"}


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除消息"""
    message = sys_message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 检查权限：只能删除自己的消息
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此消息"
        )
    
    sys_message_crud.remove(db, id=message_id)
    return {"message": "消息已删除"}


@router.delete("/batch")
async def delete_messages_batch(
    message_ids: List[int],
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量删除消息"""
    # 验证消息是否属于当前用户
    for message_id in message_ids:
        message = sys_message_crud.get(db, id=message_id)
        if not message or message.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"消息 {message_id} 不存在或无权访问"
            )
    
    # 批量删除
    count = sys_message_crud.delete_messages_batch(db, message_ids=message_ids)
    
    return {"message": f"已删除 {count} 条消息"}


@router.get("/stats/overview", response_model=MessageStatsResponse)
async def get_message_stats(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取消息统计"""
    total_count = sys_message_crud.count_by_user(db, user_id=current_user.id)
    unread_count = sys_message_crud.count_unread_by_user(db, user_id=current_user.id)
    today_count = sys_message_crud.count_today_by_user(db, user_id=current_user.id)
    
    return MessageStatsResponse(
        total_count=total_count,
        unread_count=unread_count,
        today_count=today_count
    )


@router.get("/system-users", response_model=List[dict])
async def get_system_users(
    db: Session = Depends(get_db)
):
    """获取系统用户列表（用于消息发送者信息）"""
    sys_users = sys_user_crud.get_multi(db, limit=100)
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "avatar": user.avatar,
            "introduction": user.introduction
        }
        for user in sys_users
    ]