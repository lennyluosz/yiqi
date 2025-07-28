from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os

from app.config import settings
from app.api.v1 import auth, users, activities, social, messages
from app.database import engine
from app.models import Base
from app.admin.admin import admin

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="天域同途 - 微信小程序后端API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Session中间件配置（admin需要）
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs(settings.upload_dir, exist_ok=True)

# 静态文件服务
app.mount("/static", StaticFiles(directory=settings.upload_dir), name="static")

# 注册API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(activities.router, prefix="/api/v1/activities", tags=["活动"])
app.include_router(social.router, prefix="/api/v1/social", tags=["社交"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["消息"])

# 挂载Admin界面
admin.mount_to(app)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print(f"🚀 {settings.app_name} v{settings.version} 启动成功!")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("👋 应用正在关闭...")


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "接口不存在", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.app_name} API",
        "version": settings.version,
        "docs": "/docs" if settings.debug else "文档已关闭"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )