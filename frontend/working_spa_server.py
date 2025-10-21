#!/usr/bin/env python3
"""
工作正常的SPA服务器
专门为Vue Router history模式设计
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class WorkingSPAHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加CORS头部以支持跨域
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # 解析URL路径
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        print(f"[INFO] 请求: {clean_path}")
        
        # 移除开头的斜杠，得到相对路径
        if clean_path == '/':
            file_path = 'index.html'
        else:
            file_path = clean_path.lstrip('/')
        
        # 检查文件是否存在
        full_path = os.path.join(os.getcwd(), file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # 文件存在，正常处理
            print(f"[INFO] 返回文件: {file_path}")
            self.path = clean_path
            return super().do_GET()
        
        # 文件不存在，判断是否为静态资源
        static_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.map']
        static_paths = ['/assets/', '/images/', '/static/', '/favicon']
        
        is_static_resource = (
            any(clean_path.startswith(path) for path in static_paths) or
            any(clean_path.endswith(ext) for ext in static_extensions)
        )
        
        if is_static_resource:
            # 静态资源不存在，返回404
            print(f"[INFO] 静态资源不存在: {file_path}")
            return self.send_error(404, "Static resource not found")
        
        # 非静态资源，认为是Vue路由，返回index.html
        print(f"[INFO] Vue路由，返回index.html: {clean_path}")
        
        try:
            with open('index.html', 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            print(f"[ERROR] 读取index.html失败: {e}")
            self.send_error(500, "Internal server error")

def main():
    PORT = 3001
    HOST = '0.0.0.0'
    
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(script_dir, 'dist')
    
    if not os.path.exists(dist_dir):
        print(f"❌ 错误: {dist_dir} 目录不存在")
        sys.exit(1)
    
    os.chdir(dist_dir)
    
    if not os.path.exists('index.html'):
        print("❌ 错误: index.html 不存在")
        sys.exit(1)
    
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📄 目录内容: {os.listdir('.')}")
    
    try:
        with socketserver.TCPServer((HOST, PORT), WorkingSPAHandler) as httpd:
            print(f"\n🌐 SPA服务器启动成功！")
            print(f"📱 局域网访问: http://192.168.2.70:{PORT}")
            print(f"🖥️  本机访问: http://localhost:{PORT}")
            print(f"🔄 支持Vue Router history模式")
            print(f"🐛 调试信息已启用")
            print(f"\n按 Ctrl+C 停止服务器\n")
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用")
            print("请先运行: lsof -ti :3001 | xargs kill -9")
        else:
            print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")

if __name__ == '__main__':
    main()

