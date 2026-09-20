"""
GradePilot - Local Development & Launch Assistant
Launches a local HTTP server for the GradePilot frontend.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

def main():
    print("=" * 60)
    print("🚀 Starting GradePilot Study Platform Local Server...")
    print(f"📍 Web Server Address: http://localhost:{PORT}")
    print(f"📁 Serving directory: {FRONTEND_DIR}")
    print("=" * 60)

    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down GradePilot server.")
            sys.exit(0)

if __name__ == "__main__":
    main()
