#!/usr/bin/env python3
"""
专门为Vue.js SPA应用设计的HTTP服务器
支持Vue Router的history模式
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class VueSPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析URL路径，移除查询参数
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path
        
        print(f"[DEBUG] 请求路径: {clean_path}")
        
        # 如果请求的是根路径
        if clean_path == '/':
            print("[DEBUG] 根路径请求，返回index.html")
            return self.serve_index()
        
        # 构建实际文件路径
        file_path = clean_path.lstrip('/')
        
        # 检查文件是否存在
        if os.path.isfile(file_path):
            print(f"[DEBUG] 文件存在: {file_path}")
            # 文件存在，使用父类方法正常处理
            return super().do_GET()
        
        # 文件不存在的情况
        print(f"[DEBUG] 文件不存在: {file_path}")
        
        # 如果是静态资源请求，返回404
        static_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot']
        static_paths = ['/assets/', '/images/', '/static/', '/favicon']
        
        is_static = (any(clean_path.startswith(path) for path in static_paths) or 
                    any(clean_path.endswith(ext) for ext in static_extensions))
        
        if is_static:
            print("[DEBUG] 静态资源不存在，返回404")
            return self.send_error(404, "File not found")
        
        # 其他路径都被认为是Vue路由，返回index.html
        print("[DEBUG] Vue路由请求，返回index.html")
        return self.serve_index()
    
    def serve_index(self):
        """提供index.html文件"""
        try:
            with open('index.html', 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            print("[ERROR] index.html文件不存在")
            self.send_error(404, "index.html not found")

def main():
    PORT = 3001
    HOST = '0.0.0.0'
    
    # 切换到dist目录
    if not os.path.exists('dist'):
        print("❌ 错误: dist目录不存在，请先运行 npm run build")
        sys.exit(1)
    
    os.chdir('dist')
    
    # 检查index.html是否存在
    if not os.path.exists('index.html'):
        print("❌ 错误: dist目录中找不到index.html文件")
        sys.exit(1)
    
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📄 目录内容: {', '.join(os.listdir('.'))}")
    
    # 启动服务器
    with socketserver.TCPServer((HOST, PORT), VueSPAHandler) as httpd:
        print(f"\n🌐 Vue SPA服务器启动成功！")
        print(f"📱 局域网访问: http://192.168.2.70:{PORT}")
        print(f"🖥️  本机访问: http://localhost:{PORT}")
        print(f"🔄 支持Vue Router history模式")
        print(f"🐛 调试模式已开启")
        print(f"\n按 Ctrl+C 停止服务器\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == '__main__':
    main()

