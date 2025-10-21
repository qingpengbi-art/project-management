#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户API是否正常返回所有用户
"""

import requests
import json

def test_users_api():
    """测试用户API"""
    print("🔍 测试用户API...")
    
    # 首先登录获取session
    login_url = "http://localhost:5001/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "td123456"
    }
    
    print(f"📝 登录数据: {login_data}")
    
    # 创建session以保持cookie
    session = requests.Session()
    
    try:
        # 登录
        login_response = session.post(login_url, json=login_data)
        print(f"🔐 登录响应状态: {login_response.status_code}")
        print(f"🔐 登录响应内容: {login_response.text}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get('success'):
                print("✅ 登录成功!")
                
                # 获取用户列表
                users_url = "http://localhost:5001/api/users/"
                users_response = session.get(users_url)
                
                print(f"👥 用户列表响应状态: {users_response.status_code}")
                print(f"👥 用户列表响应内容: {users_response.text}")
                
                if users_response.status_code == 200:
                    users_result = users_response.json()
                    if users_result.get('success'):
                        users = users_result.get('data', [])
                        print(f"✅ 成功获取用户列表，共 {len(users)} 个用户:")
                        
                        for i, user in enumerate(users, 1):
                            print(f"  {i}. {user.get('name')} ({user.get('username')}) - {user.get('position')} - {user.get('role')}")
                        
                        # 检查是否包含毕庆鹏
                        biqingpeng = next((u for u in users if u.get('name') == '毕庆鹏'), None)
                        if biqingpeng:
                            print("✅ 找到毕庆鹏用户:", biqingpeng)
                        else:
                            print("❌ 未找到毕庆鹏用户")
                            
                    else:
                        print(f"❌ 获取用户列表失败: {users_result.get('message')}")
                else:
                    print(f"❌ 用户列表API调用失败: {users_response.status_code}")
            else:
                print(f"❌ 登录失败: {login_result.get('message')}")
        else:
            print(f"❌ 登录请求失败: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_users_api()
