#!/usr/bin/env python3
"""
测试项目验收和维保期项目的进度计算
"""

import requests
import json

# 获取模块概览数据
url = 'http://localhost:5001/api/projects/overview'

import time
time.sleep(3)  # 等待服务启动

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # 查找波纹板项目
    for project in data.get('data', {}).get('projects', []):
        if '波纹板' in project['name']:
            print(f"\n{'='*60}")
            print(f"项目: {project['name']}")
            print(f"{'='*60}")
            print(f"状态: {project.get('status', 'N/A')}")
            print(f"API 返回的进度: {project['progress']}%")
            print(f"进度类型: {project.get('progress_type', 'N/A')}")
            print(f"进度说明: {project.get('progress_info', 'N/A')}")
            print(f"{'='*60}")
else:
    print(f"❌ API请求失败: {response.status_code}")
    print(response.text)

