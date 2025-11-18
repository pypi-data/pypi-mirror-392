"""Automated test to ensure robots.txt rules are respected."""

import asyncio
import http.server
import os
import threading
import urllib.request
from pathlib import Path
from typing import List

from mlcrawler import Crawler


class _RecordingHandler(http.server.BaseHTTPRequestHandler):
    requested_paths: List[str] = []

    def do_GET(self):  # noqa: N802 - required by BaseHTTPRequestHandler
        type(self).requested_paths.append(self.path)

        if self.path == "/robots.txt":
            self._send_response(
                "User-agent: *\nDisallow: /Security/\n",
                content_type="text/plain",
            )
        elif self.path == "/":
            html = (
                "<html><body>"
                "<h1>Welcome</h1>"
                "<a href=\"/Security/login?BackURL=%2F\">Login</a>"
                "</body></html>"
            )
            self._send_response(html)
        elif self.path.startswith("/Security/"):
            self._send_response("<html><body>Secret</body></html>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):  # noqa: A003 - inherited signature
        return

    def _send_response(self, body: str, *, content_type: str = "text/html"):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class _ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True


def test_crawler_respects_robots(tmp_path: Path):
    handler = _RecordingHandler
    handler.requested_paths = []

    server = _ThreadedHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"

    async def _run_crawl():
        crawler = Crawler(
            max_depth=1,
            follow_links=True,
            same_domain_only=True,
            obey_robots=True,
            save_to_disk=False,
            output_dir=str(tmp_path),
        )

        try:
            return await crawler.crawl(f"{base_url}/")
        finally:
            await crawler.close()

    proxy_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]
    saved_env = {var: os.environ.get(var) for var in proxy_vars}

    for var in proxy_vars:
        os.environ.pop(var, None)

    try:
        # Sanity-check the test server and reset recording state
        urllib.request.urlopen(f"{base_url}/robots.txt").read()
        handler.requested_paths = []

        pages = asyncio.run(_run_crawl())
    finally:
        for var, value in saved_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)

    requested_paths = handler.requested_paths
    assert requested_paths, "Crawler should make HTTP requests"
    assert not any(path.startswith("/Security/") for path in requested_paths)
    assert all("/Security/" not in page.url for page in pages)
    assert len(pages) == 1, "Only the root page should be processed"