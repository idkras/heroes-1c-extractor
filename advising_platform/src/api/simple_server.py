import http.server
import socketserver
import mimetypes
import os
import signal
import sys

# Добавляем правильные MIME-типы с кодировкой UTF-8
mimetypes.add_type('text/markdown; charset=utf-8', '.md')
mimetypes.add_type('text/html; charset=utf-8', '.html')

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        """Определяем MIME-тип файла по расширению"""
        if str(path).endswith('.md'):
            return 'text/plain; charset=utf-8'  # Изменено на text/plain чтобы предотвратить обработку Markdown браузером
        return super().guess_type(path)
    
    def do_GET(self):
        """Прямой доступ к файлам без преобразования в HTML"""
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Запускаем сервер на порту 5000
PORT = 5000
Handler = SimpleHTTPRequestHandler

# Обработка корректного завершения
def signal_handler(sig, frame):
    print('Завершение работы сервера...')
    try:
        if httpd:
            httpd.server_close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Попытка освободить порт, если он занят
try:
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
except OSError as e:
    if e.errno == 98:  # Address already in use
        print(f"Port {PORT} is already in use. Attempting to use a different port.")
        # Попробуем найти свободный порт
        for alt_port in range(5001, 5010):
            try:
                httpd = socketserver.TCPServer(("0.0.0.0", alt_port), Handler)
                print(f"Using alternative port {alt_port}")
                httpd.serve_forever()
                break
            except OSError:
                continue
        else:
            print("Could not find an available port. Please free port 5000 and try again.")
            sys.exit(1)
    else:
        print(f"Error starting server: {e}")
        sys.exit(1)