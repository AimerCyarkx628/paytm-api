"""
Test Script for Paytm Payment Status API
Usage:
    python test_api.py
    python test_api.py http://localhost:5000
    python test_api.py https://your-deployment.vercel.app
"""

import sys
import json
import urllib.request
import urllib.parse

# Default target (change to your deployed Vercel URL when live)
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].isalnum() else "http://localhost:5000"

# Test Credentials:
CLIENT_MID = "fzpmIb05835944940347"
CLIENT_ORDER = "T2610170101325427993215"
PAID_KEY = "demo_paid_key_vip"


def test_endpoint(title, url):
    print(f"\n[>] Testing: {title}")
    print(f"    URL: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "APITester/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.getcode()
            headers = dict(resp.info())
            body = resp.read().decode("utf-8")
            print(f"    Status Code: {status_code}")
            if "x-demo-requests-remaining" in headers:
                print(f"    Demo Requests Left: {headers['x-demo-requests-remaining']}")
            try:
                parsed = json.loads(body)
                print(f"    Response:\n{json.dumps(parsed, indent=2)}")
            except Exception:
                print(f"    Raw Response: {body}")
            return status_code == 200
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"    HTTP Error: {e.code} ({e.reason})")
        print(f"    Error Body: {body}")
        return False
    except Exception as e:
        print(f"    Request Failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print(f"PAYTM API TEST SUITE -> {TARGET_URL}")
    print("=" * 60)

    # 1. Health check
    test_endpoint("Health Check", f"{TARGET_URL}/health")

    # 2. Client Test Order (Free Demo Mode)
    test_endpoint(
        "Client Test Order Status (Free Demo)",
        f"{TARGET_URL}/?MID={CLIENT_MID}&ORDERID={CLIENT_ORDER}"
    )

    # 3. Client Test Order With Paid Key (Unlimited Access)
    test_endpoint(
        "Client Test Order (With Paid Key - Unlimited)",
        f"{TARGET_URL}/?MID={CLIENT_MID}&ORDERID={CLIENT_ORDER}&api_key={PAID_KEY}"
    )

    # 4. Error testing: Missing Order ID
    test_endpoint(
        "Validation Check (Missing ORDERID)",
        f"{TARGET_URL}/?MID={CLIENT_MID}"
    )

    print("\n" + "=" * 60)
    print("[+] Test suite finished.")
    print("=" * 60)
