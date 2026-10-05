#!/usr/bin/env python3
"""Static server for UAD 3.6 plus one endpoint: POST /api/lead stores the email gate submissions.

Leads land in /opt/openclaw/.config/dustin-os/game-leads.jsonl, one JSON object per line.
No third-party calls; wiring to GHL is a later step once Dustin supplies the webhook.
"""
import json, os, re, sys, threading, time, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
LEADS = "/opt/openclaw/.config/dustin-os/game-leads.jsonl"
WEBHOOK_FILE = "/opt/openclaw/.config/dustin-os/game-ghl-webhook"   # GoHighLevel inbound webhook URL (Lee, 2026-10-05); absent = store only


def forward_to_ghl(rec):
    """Push one lead to the GHL workflow. Runs in a thread; a failure is logged, never shown to the player."""
    try:
        url = open(WEBHOOK_FILE).read().strip()
    except OSError:
        return
    payload = {"email": rec["email"], "first_name": rec.get("name") or "", "source": "uad36-game",
               "tag": "uad-36-game", "score": rec.get("score"), "level": rec.get("level"), "won": rec.get("won"), "ts": rec["ts"]}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            sys.stderr.write("ghl %s %s\n" % (r.status, rec["email"]))
    except Exception as e:
        sys.stderr.write("ghl FAILED %s: %s\n" % (rec["email"], e))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8522
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
_recent = {}  # ip -> last post time (light rate limit)


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, fmt, *args):  # quiet: only errors + leads
        if args and str(args[0]).startswith("POST"):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    ALLOWED = ("https://game.dustinharrisos.com", "https://theappraisercoach.github.io")

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        origin = self.headers.get("Origin", "")
        if origin in self.ALLOWED:   # the GitHub Pages copy of the game posts here too
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/lead":
            return self._json(404, {"ok": False})
        ip = self.headers.get("CF-Connecting-IP") or self.client_address[0]
        now = time.time()
        if now - _recent.get(ip, 0) < 3:
            return self._json(429, {"ok": False, "error": "slow down"})
        try:
            n = min(int(self.headers.get("Content-Length", "0")), 4096)
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"ok": False, "error": "bad json"})
        email = str(data.get("email", "")).strip().lower()[:200]
        if not EMAIL_RE.match(email):
            return self._json(400, {"ok": False, "error": "That doesn't look like an email address."})
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "email": email,
            "name": str(data.get("name", "")).strip()[:100],
            "score": data.get("score"),
            "level": data.get("level"),
            "won": data.get("won"),
            "ip": ip,
            "ua": self.headers.get("User-Agent", "")[:200],
        }
        os.makedirs(os.path.dirname(LEADS), exist_ok=True)
        with open(LEADS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        _recent[ip] = now
        threading.Thread(target=forward_to_ghl, args=(rec,), daemon=True).start()
        return self._json(200, {"ok": True})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
