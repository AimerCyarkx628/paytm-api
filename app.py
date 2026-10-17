"""
Paytm Order Status API - Local / VPS Standalone Server
Run with:
    python app.py
Zero external dependencies required (uses standard library http.server).
"""

import os
import sys
from http.server import HTTPServer

# Add api directory to import the handler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))
from index import handler, DEMO_MAX_REQUESTS, PAID_API_KEYS

PORT = int(os.getenv("PORT", 5000))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, handler)
    print("=" * 60)
    print("[*] PAYTM TRANSACTION STATUS API SERVICE")
    print("=" * 60)
    print(f"Server running on   : http://localhost:{PORT}")
    print(f"Free Demo Limit     : {DEMO_MAX_REQUESTS} requests max per client IP")
    print(f"Paid Keys (Unlimited): {', '.join(PAID_API_KEYS)}")
    print("=" * 60)
    print("Example usage (Free Demo - Max 5 Requests):")
    print(f"   http://localhost:{PORT}/?MID=fzpmIb05835944940347&ORDERID=T2610170101325427993215")
    print("\nExample usage (Paid Key - Unlimited):")
    paid_key = next(iter(PAID_API_KEYS)) if PAID_API_KEYS else "YOUR_KEY"
    print(f"   http://localhost:{PORT}/?MID=fzpmIb05835944940347&ORDERID=T2610170101325427993215&api_key={paid_key}")
    print("=" * 60)
    print("Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Server stopped.")
        httpd.server_close()
