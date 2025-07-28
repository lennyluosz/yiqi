from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import UserProfile
from app.crud.user import user_crud
from app.schemas.user import UserUpdate, UserResponse
from app.utils.upload import file_upload_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    return user_crud.update_user(db, db_obj=current_user, obj_in=user_update)


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    # 验证文件类型
    if file.content_type not in file_upload_service.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )
    
    # 保存文件
    try:
        avatar_url = await file_upload_service.save_file(
            file, 
            category="avatar", 
            prefix=f"user_{current_user.id}",
            allowed_types=file_upload_service.ALLOWED_IMAGE_TYPES
        )
        
        # 删除旧头像
        if current_user.avatar:
            file_upload_service.delete_file(current_user.avatar)
        
        # 更新用户头像
        user_crud.update_user(
            db, 
            db_obj=current_user, 
            obj_in={"avatar": avatar_url}
        )
        
        return {
            "message": "头像上传成功",
            "avatar_url": avatar_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败: {str(e)}"
        )


@router.post("/upload-background")
async def upload_background(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传用户背景图"""
    # 验证文件类型
    if file.content_type not in file_upload_service.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )
    
    # 保存文件
    try:
        background_url = await file_upload_service.save_file(
            file, 
            category="image", 
            prefix=f"bg_user_{current_user.id}",
            allowed_types=file_upload_service.ALLOWED_IMAGE_TYPES
        )
        
        # 删除旧背景图
        if current_user.background:
            file_upload_service.delete_file(current_user.background)
        
        # 更新用户背景图
        user_crud.update_user(
            db, 
            db_obj=current_user, 
            obj_in={"background": background_url}
        )
        
        return {
            "message": "背景图上传成功",
            "background_url": background_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"背景图上传失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.delete("/me")
async def deactivate_current_user(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """注销当前用户账户"""
    user_crud.deactivate_user(db, user_id=current_user.id)
    return {"message": "账户已注销"}