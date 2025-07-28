#!/usr/bin/env python3
"""
测试Admin界面的脚本
"""
import requests
import time
import threading
import uvicorn
from app.main import app

def start_server():
    """在后台启动服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error")

def test_admin_access():
    """测试admin界面访问"""
    base_url = "http://localhost:8001"
    admin_url = f"{base_url}/admin/"
    
    print("🚀 启动测试服务器...")
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        print("🔍 测试admin界面访问...")
        
        # 测试根路径
        response = requests.get(base_url, timeout=5)
        print(f"✅ 根路径访问: {response.status_code}")
        
        # 测试admin路径
        response = requests.get(admin_url, timeout=5)
        print(f"✅ Admin界面访问: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 Admin界面访问成功!")
            print(f"🌐 请在浏览器中访问: {admin_url}")
            print("📝 管理员账户:")
            print("   用户名: admin")
            print("   密码: admin123456")
        else:
            print(f"❌ Admin界面访问失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_admin_access()