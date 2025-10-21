#!/usr/bin/env python3
"""
最终版本的SPA服务器 - 确保能正常工作
专门为Vue.js SPA应用设计，支持history路由模式
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class FinalSPAHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # 自定义日志输出
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        # 获取请求的路径
        url_path = urlparse(self.path).path
        print(f"[REQUEST] {url_path}")
        
        # 如果是根路径，直接提供index.html
        if url_path == '/':
            print("[RESPONSE] 返回根页面 index.html")
            return self.serve_file('index.html')
        
        # 构建文件的实际路径
        requested_file = url_path.lstrip('/')
        file_path = os.path.join(os.getcwd(), requested_file)
        
        # 检查请求的文件是否存在
        if os.path.isfile(file_path):
            print(f"[RESPONSE] 文件存在，返回: {requested_file}")
            # 文件存在，让父类处理
            return super().do_GET()
        
        # 文件不存在，判断是否为静态资源
        static_patterns = [
            '/assets/', '/images/', '/static/', '/css/', '/js/',
            '/favicon.ico', '/robots.txt', '/manifest.json'
        ]
        static_extensions = [
            '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
            '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map', '.json'
        ]
        
        is_static = (
            any(url_path.startswith(pattern) for pattern in static_patterns) or
            any(url_path.endswith(ext) for ext in static_extensions)
        )
        
        if is_static:
            print(f"[RESPONSE] 静态资源不存在: {requested_file}")
            return self.send_error(404, f"Static resource not found: {requested_file}")
        
        # 不是静态资源，认为是Vue路由，返回index.html
        print(f"[RESPONSE] Vue路由，返回 index.html: {url_path}")
        return self.serve_file('index.html')
    
    def serve_file(self, filename):
        """提供指定文件"""
        try:
            with open(filename, 'rb') as file:
                content = file.read()
            
            # 发送响应
            self.send_response(200)
            
            # 设置内容类型
            if filename.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif filename.endswith('.js'):
                content_type = 'application/javascript'
            elif filename.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'application/octet-stream'
            
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache')
            
            # 添加CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            print(f"[ERROR] 文件不存在: {filename}")
            self.send_error(404, f"File not found: {filename}")
        except Exception as e:
            print(f"[ERROR] 服务文件时出错: {e}")
            self.send_error(500, "Internal server error")

def main():
    PORT = 3001
    HOST = '0.0.0.0'
    
    # 确保在正确的目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(script_dir, 'dist')
    
    if not os.path.exists(dist_dir):
        print(f"❌ 错误: dist目录不存在 ({dist_dir})")
        print("请先运行: npm run build")
        sys.exit(1)
    
    # 切换到dist目录
    os.chdir(dist_dir)
    
    # 检查index.html是否存在
    if not os.path.exists('index.html'):
        print("❌ 错误: index.html文件不存在")
        print("请确保已正确构建项目")
        sys.exit(1)
    
    print(f"📁 服务目录: {os.getcwd()}")
    print(f"📄 文件列表: {', '.join(os.listdir('.'))}")
    
    # 启动服务器
    try:
        with socketserver.TCPServer((HOST, PORT), FinalSPAHandler) as httpd:
            print(f"\n🌐 SPA服务器启动成功！")
            print(f"📱 局域网访问: http://192.168.2.70:{PORT}")
            print(f"🖥️  本机访问: http://localhost:{PORT}")
            print(f"🔄 完全支持Vue Router history模式")
            print(f"📊 详细日志已启用")
            print(f"\n服务器运行中... 按 Ctrl+C 停止\n")
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用")
            print("解决方法: lsof -ti :3001 | xargs kill -9")
        else:
            print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")

if __name__ == '__main__':
    main()

