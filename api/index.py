import os
import json
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

# --- CONFIGURATION ---
# Max free demo requests allowed per client IP before requiring an API key
DEMO_MAX_REQUESTS = int(os.getenv("DEMO_MAX_REQUESTS", 5))

# Authorized paid API keys (comma-separated list in environment)
# Paid keys get UNLIMITED requests and bypass the 5-request demo limit
PAID_API_KEYS = set(
    k.strip() for k in os.getenv("API_KEYS", "demo_paid_key_vip,client_live_key").split(",") if k.strip()
)

# Upstream Gateway URL (strictly kept internal and never leaked in headers or errors)
PAYTM_STATUS_URL = "https://securegw.paytm.in/merchant-status/getTxnStatus"

# In-memory IP tracking for demo requests
demo_ip_counts = {}


def get_client_ip(handler_instance) -> str:
    """Extracts client IP address safely from Vercel / Cloud proxy headers."""
    # 1. Standard Cloud / Vercel forwarded IP
    x_forwarded = handler_instance.headers.get("x-forwarded-for")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()

    # 2. Real IP header
    x_real = handler_instance.headers.get("x-real-ip")
    if x_real:
        return x_real.strip()

    # 3. Direct socket address
    if hasattr(handler_instance, "client_address") and handler_instance.client_address:
        return str(handler_instance.client_address[0])

    return "127.0.0.1"


def verify_client_access(client_ip: str, provided_key: str | None) -> tuple[bool, str, int]:
    """
    Checks if client is allowed to make a request.
    Returns: (is_allowed, reason, remaining_demo_requests)
    """
    # 1. Paid / Authorized Key -> Unlimited requests
    if provided_key and provided_key in PAID_API_KEYS:
        return True, "PAID_UNLIMITED", 999999

    # 2. Demo User (No key or free test key) -> Enforce 5 requests max
    current_count = demo_ip_counts.get(client_ip, 0)
    if current_count >= DEMO_MAX_REQUESTS:
        return False, f"Demo limit reached ({DEMO_MAX_REQUESTS}/{DEMO_MAX_REQUESTS} requests used). Contact admin to get your API Key.", 0

    demo_ip_counts[client_ip] = current_count + 1
    remaining = DEMO_MAX_REQUESTS - demo_ip_counts[client_ip]
    return True, "DEMO_ALLOWED", remaining


def query_gateway(mid: str, order_id: str) -> dict:
    """
    Calls payment gateway while completely sanitizing internal details.
    Zero backend URLs or internal traces are ever exposed to the client.
    """
    try:
        payload = json.dumps({"MID": mid, "ORDERID": order_id})
        data = urllib.parse.urlencode({"JsonData": payload}).encode("utf-8")

        req = urllib.request.Request(
            PAYTM_STATUS_URL,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            resp_body = response.read().decode("utf-8")
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        # Sanitize: Never leak upstream URLs or server traces
        return {
            "STATUS": "TXN_FAILURE",
            "RESPCODE": str(e.code),
            "RESPMSG": "Verification temporary service error."
        }
    except Exception:
        # Sanitize: Never leak Python tracebacks or internal endpoints
        return {
            "STATUS": "TXN_FAILURE",
            "RESPCODE": "500",
            "RESPMSG": "Service connection error."
        }


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function HTTP Handler.
    Masks internal server signatures to protect backend details in Network Tab.
    """
    server_version = "Gateway"
    sys_version = ""

    def _set_headers(self, status=200, remaining=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, Authorization")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        if remaining is not None and remaining < 999999:
            self.send_header("X-Demo-Requests-Remaining", str(remaining))
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self._set_headers(200)

    def do_GET(self):
        """Handles GET requests: /?MID=...&ORDERID=...&api_key=..."""
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)

        # Health check
        if parsed_url.path in ("/health", "/status"):
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy"}).encode("utf-8"))
            return

        client_ip = get_client_ip(self)
        provided_key = (
            query.get("api_key", [None])[0]
            or query.get("key", [None])[0]
            or self.headers.get("X-API-Key")
        )

        # 1. Rate Limit & Demo Protection Check (Max 5 Requests for Demo)
        allowed, reason, remaining = verify_client_access(client_ip, provided_key)
        if not allowed:
            self._set_headers(429, remaining=0)
            response = {
                "STATUS": "TXN_FAILURE",
                "RESPCODE": "429",
                "RESPMSG": reason
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # 2. Parameter Validation
        mid = query.get("MID", [None])[0] or query.get("mid", [None])[0]
        order_id = query.get("ORDERID", [None])[0] or query.get("orderid", [None])[0] or query.get("order_id", [None])[0]

        if not mid:
            self._set_headers(200, remaining=remaining)
            self.wfile.write(json.dumps({"RESPCODE": "335", "RESPMSG": "Mid is invalid"}).encode("utf-8"))
            return

        if not order_id:
            self._set_headers(200, remaining=remaining)
            self.wfile.write(json.dumps({"ErrorCode": "VAER-PF111", "ErrorMsg": "ORDER ID IS REQUIRED"}).encode("utf-8"))
            return

        # 3. Query Gateway cleanly
        result = query_gateway(mid.strip(), order_id.strip())
        self._set_headers(200, remaining=remaining)
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def do_POST(self):
        """Handles POST requests cleanly."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
        
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)

        client_ip = get_client_ip(self)
        provided_key = (
            query.get("api_key", [None])[0]
            or query.get("key", [None])[0]
            or self.headers.get("X-API-Key")
        )

        allowed, reason, remaining = verify_client_access(client_ip, provided_key)
        if not allowed:
            self._set_headers(429, remaining=0)
            response = {
                "STATUS": "TXN_FAILURE",
                "RESPCODE": "429",
                "RESPMSG": reason
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        mid, order_id = None, None
        try:
            json_data = json.loads(body)
            mid = json_data.get("MID") or json_data.get("mid")
            order_id = json_data.get("ORDERID") or json_data.get("orderid") or json_data.get("order_id")
        except Exception:
            parsed_form = urllib.parse.parse_qs(body)
            mid = parsed_form.get("MID", [None])[0]
            order_id = parsed_form.get("ORDERID", [None])[0]

        if not mid:
            self._set_headers(200, remaining=remaining)
            self.wfile.write(json.dumps({"RESPCODE": "335", "RESPMSG": "Mid is invalid"}).encode("utf-8"))
            return

        if not order_id:
            self._set_headers(200, remaining=remaining)
            self.wfile.write(json.dumps({"ErrorCode": "VAER-PF111", "ErrorMsg": "ORDER ID IS REQUIRED"}).encode("utf-8"))
            return

        result = query_gateway(mid.strip(), order_id.strip())
        self._set_headers(200, remaining=remaining)
        self.wfile.write(json.dumps(result).encode("utf-8"))
