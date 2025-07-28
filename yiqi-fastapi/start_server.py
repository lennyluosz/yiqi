#!/usr/bin/env python3
"""
启动一起呦FastAPI服务器的脚本
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 正在启动一起呦FastAPI服务器...")
    print("📋 服务信息:")
    print("   - API文档: http://localhost:8001/docs")
    print("   - 管理后台: http://localhost:8001/YiqiAdmin0001shujian/")
    print("   - 管理员账户: admin / admin123456")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )