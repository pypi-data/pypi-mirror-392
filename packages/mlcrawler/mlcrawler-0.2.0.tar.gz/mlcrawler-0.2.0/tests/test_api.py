import asyncio
import os
import threading
import http.server
import socketserver
from pathlib import Path

import pytest
from mlcrawler.api import Crawler


# Disable proxy for all tests - proxies interfere with localhost test server
@pytest.fixture(scope="session", autouse=True)
def disable_proxy():
    """Remove proxy environment variables for the test session."""
    for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
        os.environ.pop(key, None)


# Fixture to run a simple HTTP server in a separate thread
@pytest.fixture(scope="session")
def static_server():
    PORT = 0  # Use a random available port
    ASSETS_DIR = Path(__file__).parent / "assets"

    Handler = http.server.SimpleHTTPRequestHandler

    # Change directory to serve files from the correct path
    class MyHandler(Handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ASSETS_DIR), **kwargs)

    # Allow address reuse to prevent "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), MyHandler)
    actual_port = httpd.server_address[1]  # Get the actual port assigned
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    yield f"http://localhost:{actual_port}"
    httpd.shutdown()


def test_fetch_single_page_no_save(static_server):
    """
    Tests that the crawler can fetch a single page without saving it.
    """
    url = f"{static_server}/index.html"

    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=False,  # Don't follow links in this simple test
    )

    # Run the async crawler in a sync test
    results = asyncio.run(crawler.crawl(url=url))

    assert len(results) == 1
    page = results[0]

    assert page.url == url
    assert page.status_code == 200
    assert "<h1>Welcome</h1>" in page.html
    assert page.markdown is not None
    assert "Welcome" in page.markdown

    # Verify markdown content
    assert len(page.markdown) > 0
    assert "Test Page" in page.markdown  # The title from the HTML


def test_follow_links_unlimited(static_server):
    """
    Tests that the crawler can follow links and fetch all reachable pages.
    The linked/ directory has 10 pages (page0-page9) with various links.
    """
    url = f"{static_server}/linked/page0.html"

    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        max_depth=0,  # Unlimited depth
        max_pages=0,  # Unlimited pages
    )

    # Run the crawler
    results = asyncio.run(crawler.crawl(url=url))

    # Should fetch all 10 pages
    assert len(results) == 10, f"Expected 10 pages, got {len(results)}"

    # Extract URLs and titles
    urls = {page.url for page in results}
    titles = {page.title for page in results}

    # Check that all pages were fetched (page0 through page9)
    for i in range(10):
        expected_url = f"{static_server}/linked/page{i}.html"
        assert expected_url in urls, f"Missing page{i}.html"
        assert f"Page {i}" in titles, f"Missing title for page {i}"

    # Verify no duplicates (set length should equal list length)
    assert len(urls) == len(results), "Found duplicate pages in results"


def test_follow_links_handles_duplicates(static_server):
    """
    Tests that the crawler properly handles duplicate links without
    fetching the same page multiple times.
    """
    url = f"{static_server}/linked/page0.html"

    # Track all URLs the crawler attempts to fetch
    fetched_urls = []

    async def track_fetches(page):
        fetched_urls.append(page.url)

    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        max_depth=0,
    )

    # Use the event handler to track fetches
    @crawler.on("page")
    async def page_handler(page):
        await track_fetches(page)

    # Run the crawler
    results = asyncio.run(crawler.crawl(url=url))

    # Should fetch exactly 10 unique pages despite duplicate links
    assert len(results) == 10
    assert len(fetched_urls) == 10

    # Verify all fetched URLs are unique
    unique_urls = set(fetched_urls)
    assert len(unique_urls) == 10, "Crawler fetched the same page multiple times"


def test_follow_links_max_pages_limit(static_server):
    """
    Tests that the crawler respects max_pages limit.
    """
    url = f"{static_server}/linked/page0.html"

    # Limit to 5 pages
    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        max_pages=5,
    )

    results = asyncio.run(crawler.crawl(url=url))

    # Should stop at 5 pages
    assert len(results) == 5, f"Expected 5 pages, got {len(results)}"

    # Verify all results are unique
    urls = {page.url for page in results}
    assert len(urls) == 5, "Found duplicate pages in results"


def test_follow_links_max_depth_limit(static_server):
    """
    Tests that the crawler respects max_depth limit.
    Starting from page0, depth 0 = page0, depth 1 = page1,page2, etc.
    """
    url = f"{static_server}/linked/page0.html"

    # Limit depth to 1 (seed + 1 level of links)
    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        max_depth=1,
    )

    results = asyncio.run(crawler.crawl(url=url))

    # Depth 0: page0
    # Depth 1: page1, page2 (linked from page0)
    # Should not fetch page3, page4, etc (depth 2)
    assert (
        len(results) <= 3
    ), f"Expected at most 3 pages with depth=1, got {len(results)}"

    # Check depths
    for page in results:
        assert page.depth <= 1, f"Page {page.url} has depth {page.depth}, expected <= 1"


def test_robots_txt_obey_true(static_server):
    """
    Tests that the crawler respects robots.txt when obey_robots=True.
    The robots.txt file disallows /denied.html.
    """
    url = f"{static_server}/index.html"

    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        obey_robots=True,  # Obey robots.txt
    )

    results = asyncio.run(crawler.crawl(url=url))

    # Extract all fetched URLs
    urls = {page.url for page in results}

    # Should fetch index.html and page1.html
    assert f"{static_server}/index.html" in urls
    assert f"{static_server}/page1.html" in urls

    # Should NOT fetch denied.html (blocked by robots.txt)
    denied_url = f"{static_server}/denied.html"
    assert (
        denied_url not in urls
    ), f"Crawler fetched {denied_url} despite robots.txt disallow"


def test_robots_txt_obey_false(static_server):
    """
    Tests that the crawler ignores robots.txt when obey_robots=False.
    The robots.txt file disallows /denied.html, but it should still be fetched.
    """
    url = f"{static_server}/index.html"

    crawler = Crawler(
        save_to_disk=False,
        cache_mode="bypass",
        follow_links=True,
        obey_robots=False,  # Ignore robots.txt
    )

    results = asyncio.run(crawler.crawl(url=url))

    # Extract all fetched URLs
    urls = {page.url for page in results}

    # Should fetch all pages including denied.html
    assert f"{static_server}/index.html" in urls
    assert f"{static_server}/page1.html" in urls

    # Should fetch denied.html even though robots.txt disallows it
    denied_url = f"{static_server}/denied.html"
    assert (
        denied_url in urls
    ), f"Crawler should fetch {denied_url} when obey_robots=False"

    # Verify denied page content
    denied_page = next(p for p in results if p.url == denied_url)
    assert denied_page.status_code == 200
    assert "Access Denied by robots.txt" in denied_page.html
