#!/usr/bin/env python3
"""
测试Admin界面列表页面的脚本
"""
import requests
import time
import threading
import uvicorn
from app.main import app

def start_server():
    """在后台启动服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="error")

def test_admin_lists():
    """测试admin列表页面访问"""
    base_url = "http://localhost:8002"
    admin_base_url = f"{base_url}/admin"
    
    # 要测试的列表页面
    test_pages = [
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
    
    print("🚀 启动测试服务器...")
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        print("🔍 测试admin列表页面访问...")
        
        # 创建session以保持认证状态
        session = requests.Session()
        
        # 先访问登录页面
        login_url = f"{admin_base_url}/login"
        response = session.get(login_url, timeout=5)
        print(f"📝 登录页面访问: {response.status_code}")
        
        # 模拟登录 (这里简化处理，实际需要处理CSRF等)
        # login_data = {
        #     "username": "admin",
        #     "password": "admin123456"
        # }
        # response = session.post(login_url, data=login_data, timeout=5)
        
        # 测试各个列表页面（无需认证的测试）
        success_count = 0
        failed_pages = []
        
        for page in test_pages:
            try:
                url = f"{admin_base_url}/{page}"
                response = session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {page}: 访问成功")
                    success_count += 1
                elif response.status_code == 302:  # 重定向到登录页面
                    print(f"🔐 {page}: 需要登录 (正常)")
                    success_count += 1
                else:
                    print(f"❌ {page}: HTTP {response.status_code}")
                    failed_pages.append((page, response.status_code))
                    
            except Exception as e:
                print(f"❌ {page}: 请求失败 - {e}")
                failed_pages.append((page, str(e)))
        
        print(f"\n📊 测试结果:")
        print(f"   成功: {success_count}/{len(test_pages)}")
        if failed_pages:
            print(f"   失败页面: {failed_pages}")
        else:
            print("   🎉 所有页面测试通过!")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_admin_lists()