
import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from .gen_doc import generate_web_docs

class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # 重写这个方法来抑制日志输出
        pass
    
def find_available_port():
    # 创建一个socket对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 使得端口可以被重用
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定到地址和端口,但端口设置为0,让系统自动分配一个可用的端口
    sock.bind(('', 0))
    # 获取绑定的地址和端口
    host, port = sock.getsockname()
    # 关闭socket
    sock.close()
    return port

def start_http_server(config):
    # 切换到指定的目录
    directory = os.path.join(os.getcwd(), config['html_folder'])
    port = find_available_port()

    # 创建 HTTP 服务器
    with HTTPServer(('', port), SilentHTTPRequestHandler) as httpd:
        print(f"\nZood live server: http://127.0.0.1:{httpd.server_address[1]}/docs/index.html")
        httpd.RequestHandlerClass.directory = directory
        # 创建一个线程来运行服务器
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        try:
            while True:
                command = input("Press 'r' to regenerate docs or 'q' to quit: ")
                if command.lower() == 'r':
                    generate_web_docs(config)
                elif command.lower() == 'q':
                    break
        except KeyboardInterrupt:
            print("\nServer is shutting down...")

        httpd.shutdown()
        server_thread.join()  # 等待服务器线程退出
        print("Server closed.")