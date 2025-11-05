#!/usr/bin/env python3
"""
测试Dashboard API返回的进度
"""

import requests
import json

# 获取Dashboard数据
url = 'http://localhost:5001/api/projects/overview'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # 查找电池仓项目
    for project in data.get('data', {}).get('projects', []):
        if '电池仓' in project['name']:
            print(f"\n{'='*60}")
            print(f"项目: {project['name']}")
            print(f"{'='*60}")
            print(f"状态: {project['status']}")
            print(f"Dashboard API 返回的进度: {project['progress']}%")
            print(f"进度类型: {project.get('progress_type', 'N/A')}")
            print(f"进度说明: {project.get('progress_info', 'N/A')}")
            print(f"项目来源: {project.get('project_source', 'N/A')}")
            print(f"{'='*60}\n")
            break
    else:
        print("❌ 未找到电池仓项目")
else:
    print(f"❌ API请求失败: {response.status_code}")
    print(response.text)

