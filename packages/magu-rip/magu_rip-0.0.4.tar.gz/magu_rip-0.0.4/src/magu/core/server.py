from http.server import HTTPServer
from magu.services.handler import Handler
from magu.core.router import Router
import magu.properties as properties
import json

class ServerHandler(Handler):
    router = Router()

    def do_GET(self):
        self.router.route(self, 'GET')
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            body = self.rfile.read(length)
            data = json.loads(body)

        self.router.route(self, 'POST', data=data)

    def do_PUT(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            body = self.rfile.read(length)
            data = json.loads(body)

        self.router.route(self, 'PUT', data=data)
    
    def do_PATCH(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            body = self.rfile.read(length)
            data = json.loads(body)

        self.router.route(self,'PATCH', data=data)

    def do_DELETE(self):
        self.router.route(self,'DELETE')
        

def run_server():
    httpd = HTTPServer((properties.SERVER_HOST, properties.SERVER_PORT), ServerHandler)
    print(f"[Server] Server running on {properties.SERVER_ADDRESS}")
    httpd.serve_forever()
