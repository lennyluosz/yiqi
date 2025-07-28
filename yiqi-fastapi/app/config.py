from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # 应用基础配置
    app_name: str = "天域同途"
    version: str = "2.0.0"
    debug: bool = True
    secret_key: str
    
    # 数据库配置
    database_url: str
    
    # Redis配置  
    redis_url: str = "redis://localhost:6379/0"
    
    # 微信小程序配置
    wechat_app_id: str
    wechat_app_secret: str
    
    # JWT配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    # CORS配置
    allowed_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()