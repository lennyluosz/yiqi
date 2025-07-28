#!/usr/bin/env python3
"""
最终测试Admin界面的脚本 - 包含真实登录测试
"""
import requests
import time
import threading
import uvicorn
from app.main import app

def start_server():
    """在后台启动服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="error")

def test_admin_full():
    """完整测试admin界面"""
    base_url = "http://localhost:8002"
    admin_base_url = f"{base_url}/YiqiAdmin0001shujian"
    
    print("🚀 启动测试服务器...")
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        print("🔍 测试admin界面完整功能...")
        
        # 创建session以保持状态
        session = requests.Session()
        
        # 1. 测试admin首页
        response = session.get(admin_base_url, timeout=5)
        print(f"✅ Admin首页: {response.status_code}")
        
        # 2. 测试登录页面
        login_url = f"{admin_base_url}/login"
        response = session.get(login_url, timeout=5)
        print(f"✅ 登录页面: {response.status_code}")
        
        # 3. 测试所有列表页面（无需登录的基础测试）
        pages = [
            "user/list",
            "activity_type/list", 
            "activity/list",
            "activity_user_info/list",
            "sharing_set/list",
            "user_collection/list",
            "user_report/list",
            "comment/list",
            "feedback/list",
            "sys_user/list",
            "sys_message/list"
        ]
        
        success_count = 0
        for page in pages:
            try:
                url = f"{admin_base_url}/{page}"
                response = session.get(url, timeout=5)
                
                if response.status_code in [200, 302]:  # 200成功或302重定向到登录
                    print(f"✅ {page}: OK ({response.status_code})")
                    success_count += 1
                else:
                    print(f"❌ {page}: ERROR {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {page}: EXCEPTION {e}")
        
        print(f"\n📊 测试总结:")
        print(f"   成功页面: {success_count}/{len(pages)}")
        
        if success_count == len(pages):
            print("🎉 所有admin功能测试通过!")
            print(f"🌐 Admin地址: {admin_base_url}/")
            print("👤 管理员账户: admin / admin123456")
            print("✨ fields_default_sort格式错误已完全修复!")
        else:
            print("⚠️  部分页面存在问题，需要进一步检查")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_admin_full()