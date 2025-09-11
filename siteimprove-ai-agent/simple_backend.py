#!/usr/bin/env python3
"""
Simple backend server for Siteimprove AI Agent
Lightweight version without heavy dependencies
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class SiteimproveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        if parsed_path.path == '/api/status':
            response = {
                "status": "running",
                "message": "Siteimprove AI Agent Backend is running",
                "timestamp": time.time()
            }
        elif parsed_path.path == '/api/broken-links':
            # Mock data for demonstration
            response = {
                "data": [
                    {
                        "page_url": "https://example.com/page1",
                        "broken_link": "https://broken-link.com/404",
                        "clicks": 25,
                        "page_views": 150,
                        "priority_score": 8.5
                    },
                    {
                        "page_url": "https://example.com/page2", 
                        "broken_link": "https://another-broken.com/missing",
                        "clicks": 12,
                        "page_views": 89,
                        "priority_score": 6.2
                    }
                ],
                "total": 2,
                "status": "success"
            }
        else:
            response = {"error": "Endpoint not found", "status": 404}
            
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/prompt':
            try:
                data = json.loads(post_data.decode())
                prompt = data.get('prompt', '')
                
                # Simple prompt processing
                response = {
                    "message": f"Processed command: {prompt}",
                    "action": "mock_action",
                    "status": "success",
                    "data": {
                        "command_understood": True,
                        "next_steps": ["Login to Siteimprove", "Navigate to broken links", "Extract data"]
                    }
                }
            except json.JSONDecodeError:
                response = {"error": "Invalid JSON", "status": "error"}
        else:
            response = {"error": "Endpoint not found", "status": 404}
            
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log message"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SiteimproveHandler)
    
    print(f"🚀 Siteimprove AI Agent Backend Server")
    print(f"📡 Server running on http://localhost:{port}")
    print(f"🔗 API Endpoints:")
    print(f"   GET  /api/status - Server status")
    print(f"   GET  /api/broken-links - Get broken links data")
    print(f"   POST /api/prompt - Process natural language commands")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
