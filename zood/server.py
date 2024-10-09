
import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from .gen_doc import generate_web_docs, chdir_md

class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # 重写这个方法来抑制日志输出
        pass

def find_available_port(start_port=8000, end_port=8100):
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:  # 端口可用
                return port
    raise Exception("No available ports found in the specified range.")

def start_http_server(config):
    # 切换到指定的目录
    directory = config['html_folder']
    port = find_available_port()
    os.chdir(directory)

    # 创建 HTTP 服务器
    with HTTPServer(('', port), SilentHTTPRequestHandler) as httpd:
        print(f"\nZood live server: http://127.0.0.1:{port}")

        # 创建一个线程来运行服务器
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.start()

        try:
            while True:
                command = input("Press 'r' to regenerate docs or 'q' to quit: ")
                if command.lower() == 'r':
                    chdir_md(config['markdown_folder'])
                    generate_web_docs(config)
                elif command.lower() == 'q':
                    break
        except KeyboardInterrupt:
            print("\nServer is shutting down...")

        httpd.shutdown()
        server_thread.join()  # 等待服务器线程退出
        print("Server closed.")
        
    # if regenerate_docs:
    #     # clear screen
    #     os.system('cls' if os.name == 'nt' else 'clear')
        
    #     start_http_server(config)