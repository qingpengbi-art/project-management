#!/usr/bin/env python3
"""
简单的SPA静态文件服务器
支持Vue Router的history模式
"""

import http.server
import socketserver
import os
import mimetypes
from urllib.parse import urlparse

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析请求路径
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 如果是API请求，返回404
        if path.startswith('/api/'):
            self.send_error(404)
            return
            
        # 构建文件路径
        if path == '/':
            file_path = 'index.html'
        else:
            file_path = path.lstrip('/')
            
        # 检查文件是否存在
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # 文件存在，正常处理
            super().do_GET()
        else:
            # 文件不存在，检查是否是静态资源
            if any(path.startswith(prefix) for prefix in ['/assets/', '/images/', '/favicon']):
                # 静态资源不存在，返回404
                self.send_error(404)
                return
            else:
                # 可能是Vue路由，返回index.html
                # 读取并发送index.html内容
                try:
                    with open('index.html', 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404)

def run_server(port=3001, host='0.0.0.0'):
    """启动SPA服务器"""
    os.chdir('dist')
    
    # 获取本机IP地址
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.2.70"  # 默认IP
    
    with socketserver.TCPServer((host, port), SPAHandler) as httpd:
        print(f"🌐 SPA服务器启动成功")
        print(f"📱 局域网访问: http://{local_ip}:{port}")
        print(f"🖥️  本机访问: http://localhost:{port}")
        print(f"按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == '__main__':
    run_server()
