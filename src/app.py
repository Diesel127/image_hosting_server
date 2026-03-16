import http.server
import os
import socketserver


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            '/': 'index.html',
            '/upload': 'upload.html',
            '/images-list': 'images.html'
        }

        if self.path in routes:
            self.serve_template(routes[self.path])
        elif self.path.startswith('/static/'):
            self.serve_static(self.path)
        elif self.path.startswith('/api/images'):
            self.handle_get_images()
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    port = int(os.environ.get('PORT', port))
    #db.connect()
    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            print(f"Server running on port {port} ...")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server stopped by user")
    except OSError as e:
        if e.errno == 48:
            print(f"Port {port} is already in use. Please stop the server | lsof -ti :{port} | xargs kill -9")
        else:
            print(f"Error starting server: {e}")
    # finally:
    #     db.disconnect()


if __name__ == "__main__":
    run_server()