from http.server import BaseHTTPRequestHandler
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "<h1>GraphOne / FrontierAtlas AI Intelligence Pipeline</h1><p>Pipeline engine and API active.</p>"
            
        self.wfile.write(content.encode('utf-8'))
        return
