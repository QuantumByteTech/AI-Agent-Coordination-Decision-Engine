"""
Local development server for the standalone frontend.

It serves the frontend files and transparently proxies /api/* and /health
to the FastAPI backend running on http://127.0.0.1:8000.

No backend changes or CORS configuration are required.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

BACKEND = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _proxy(self):
        target = BACKEND + self.path
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None

        req = Request(
            target,
            data=body,
            method=self.command,
            headers={
    "Content-Type": self.headers.get("Content-Type", "application/json"),
    "Accept": self.headers.get("Accept", "application/json"),
    "Authorization": self.headers.get("Authorization", ""),
},
        )

        try:
            with urlopen(req, timeout=30) as response:
                data = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except URLError as e:
            data = ('{"detail":"Backend unavailable: %s"}' % str(e.reason)).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/") or self.path == "/health":
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(404)

    def log_message(self, format, *args):
        print("[frontend]", format % args)


if __name__ == "__main__":
    print("AI HR Frontend")
    print("Open: http://127.0.0.1:5500")
    print("Backend expected: http://127.0.0.1:8000")
    ThreadingHTTPServer(("127.0.0.1", 5500), Handler).serve_forever()
