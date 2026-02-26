"""
Minimal HTTP server for testing - no background threads
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from shared_data import dashboard_data

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "status": "System Online - Minimal Mode",
                "endpoints": {
                    "/": "System status",
                    "/api/dashboard": "Dashboard data"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/api/dashboard":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(dashboard_data, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[REQUEST] {format % args}")

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print("=" * 60)
    print("🏥 Neonatal Cry Detection System - MINIMAL MODE")
    print("=" * 60)
    print(f"🚀 Server running on http://127.0.0.1:{port}")
    print(f"📊 Dashboard API: http://127.0.0.1:{port}/api/dashboard")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
