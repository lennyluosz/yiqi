from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from app.database import get_db
from app.core.auth import create_access_token, get_wechat_session_key, get_current_active_user
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserResponse, Token
from app.models.user import UserProfile
from app.schemas.auth import WechatLoginRequest

router = APIRouter()


@router.post("/wechat-login", response_model=Dict[str, Any])
async def wechat_login(
    login_data: WechatLoginRequest,
    db: Session = Depends(get_db)
):
    """微信小程序登录"""
    try:
        # 获取微信session_key和openid
        wechat_data = await get_wechat_session_key(login_data.code)
        openid = wechat_data.get("openid")
        
        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取微信用户信息失败"
            )
        
        # 检查用户是否已存在
        user = user_crud.get_by_openid(db, openid=openid)
        
        if not user:
            # 创建新用户
            user_data = UserCreate(
                openid=openid,
                nick_name=login_data.user_info.nick_name,
                avatar_url=login_data.user_info.avatar_url,
                gender=login_data.user_info.gender,
                country=login_data.user_info.country,
                province=login_data.user_info.province,
                city=login_data.user_info.city,
                language=login_data.user_info.language,
                user_bh=uuid.uuid4().hex,
                name=login_data.user_info.nick_name or f"用户{openid[:8]}"
            )
            user = user_crud.create(db, obj_in=user_data)
        else:
            # 更新用户信息
            update_data = {
                "nick_name": login_data.user_info.nick_name,
                "avatar_url": login_data.user_info.avatar_url,
                "country": login_data.user_info.country,
                "province": login_data.user_info.province,
                "city": login_data.user_info.city,
                "language": login_data.user_info.language,
            }
            user = user_crud.update(db, db_obj=user, obj_in=update_data)
        
        # 生成JWT令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "nick_name": user.nick_name,
                "avatar_url": user.avatar_url,
                "user_bh": user.user_bh
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """刷新访问令牌"""
    access_token = create_access_token(data={"sub": str(current_user.id)})
    return Token(access_token=access_token, token_type="bearer")