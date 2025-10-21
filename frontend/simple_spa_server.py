#!/usr/bin/env python3
"""
简单可靠的SPA服务器
专门为Vue Router的history模式设计
"""

import http.server
import socketserver
import os
import sys

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 获取请求路径
        path = self.path.split('?')[0]  # 移除查询参数
        
        print(f"请求路径: {path}")  # 调试信息
        
        # 如果是根路径，直接返回index.html
        if path == '/':
            return super().do_GET()
        
        # 如果是静态资源文件，正常处理
        if (path.startswith('/assets/') or 
            path.startswith('/images/') or 
            path.startswith('/favicon') or
            path.endswith('.js') or 
            path.endswith('.css') or 
            path.endswith('.png') or 
            path.endswith('.jpg') or 
            path.endswith('.ico')):
            return super().do_GET()
        
        # 其他所有路径都返回index.html（SPA路由）
        self.path = '/'
        return super().do_GET()

def main():
    PORT = 3001
    HOST = '0.0.0.0'
    
    # 切换到dist目录
    os.chdir('dist')
    
    # 检查index.html是否存在
    if not os.path.exists('index.html'):
        print("❌ 错误: 找不到index.html文件")
        sys.exit(1)
    
    print(f"📁 当前工作目录: {os.getcwd()}")
    print(f"📄 文件列表: {os.listdir('.')}")
    
    with socketserver.TCPServer((HOST, PORT), SPAHandler) as httpd:
        print(f"🌐 SPA服务器启动成功")
        print(f"📱 局域网访问: http://192.168.2.70:{PORT}")
        print(f"🖥️  本机访问: http://localhost:{PORT}")
        print(f"🔄 支持Vue Router的history模式")
        print(f"按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == '__main__':
    main()

