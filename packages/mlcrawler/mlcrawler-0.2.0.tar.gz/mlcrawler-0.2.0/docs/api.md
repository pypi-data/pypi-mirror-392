# API Reference

This page documents the public library API for `mlcrawler`.

> The canonical and more extensive API documentation is available in `API.md` at the project root; this page is a curated version suitable for the docs site.

## Public imports

```python
from mlcrawler import Crawler, Page
```

## Crawler

`Crawler` is the main entry point. It is an async-first, callback-driven class used to configure and run crawls.

Constructor highlights:

- `user_agent` (str) - User agent string for HTTP requests
- `follow_redirects` (bool) - Whether to follow HTTP redirects (default: False)
- `max_depth` (int) - Maximum crawl depth (0 = unlimited)
- `max_pages` (int) - Maximum pages to crawl (0 = unlimited)
- `main_article_only` (bool) - Extract main content only using trafilatura
- `cache_dir` (str) - Directory for caching HTTP responses
- `cache_mode` (str) - Cache behavior: "conditional" (default), "force", "bypass", or "offline"
- `cache_ttl` (int) - Cache TTL in seconds for resources without validators
- `follow_links` (bool) - Whether to discover and follow links
- `same_domain_only` (bool) - Restrict crawling to same domain
- `obey_robots` (bool) - Respect robots.txt
- `rate_limit_ms` (int) - Per-host delay in milliseconds
- `concurrency` (int) - Global concurrent request limit
- `per_host_concurrency` (int) - Per-host concurrent request limit
- `include_patterns` / `exclude_patterns` (List[str]) - URL regex patterns for filtering
- `remove_selectors` (List[str]) - CSS selectors to remove from HTML
- `save_to_disk` (bool) - Save markdown files to disk
- `output_dir` (str) - Output directory for saved files

### Methods

- `crawl(url, callback=None, follow_links=None) -> List[Page]` — Crawl a seed URL and return collected Page objects.
- `crawl_many(urls, callback=None, follow_links=None) -> List[Page]` — Crawl multiple seeds.
- `crawl_sitemap(sitemap_url, callback=None) -> List[Page]` — Discover URLs in a sitemap and crawl them.
- `stream(url, follow_links=None) -> AsyncIterator[Page]` — Async generator yielding `Page` objects as they are processed.
- `on(event)` — Decorator to register event handlers for `fetch`, `page`, `error`, and `complete`.
- `from_config(config_files, **overrides)` — Classmethod to construct a `Crawler` from TOML config files.

### Events

```python
@crawler.on("fetch")
async def on_fetch(url: str):
    """Called before fetching a URL."""
    ...

@crawler.on("page")
async def on_page(page: Page):
    """Called after processing a page."""
    ...

@crawler.on("error")
async def on_error(url: str, error: Exception):
    """Called when an error occurs."""
    ...

@crawler.on("complete")
async def on_complete(stats: dict):
    """Called when crawl completes."""
    ...
```

## Configuration Options

### HTTP Behavior

- `follow_redirects` - Control HTTP redirect behavior (default: `false`)
  - `false` - Don't follow redirects, return redirect response
  - `true` - Follow redirects to final destination

### Cache Modes

The crawler supports multiple caching strategies:

- **`conditional`** (default) - Use cache with conditional GET requests
  - Sends `If-None-Match` / `If-Modified-Since` headers
  - Reuses cached content on 304 Not Modified
  - Updates cache on successful fetch

- **`force`** - Always use cache, never make HTTP requests
  - Serves only from cache
  - Skips URLs not in cache

- **`bypass`** - Always fetch from network
  - Ignores existing cache
  - Updates cache with fresh content

- **`offline`** - Use cache if available, skip if not
  - No HTTP requests at all
  - Useful for rate-limited or offline scenarios

### Cache TTL

For resources without proper cache validators (ETag/Last-Modified), the crawler uses age-based caching:

- `cache_ttl` - Time-to-live in seconds (default: 3600)
- Cached content older than TTL is refetched
- Resources with validators always use conditional requests

### Cache File Structure

The cache uses real URL paths (not hashes) with a `.cache` suffix to prevent file/directory collisions:

```
.cache/mlcrawler/
└── example.com/
    ├── index.html.cache          # Cached HTML file
    ├── index.html.meta.json      # Metadata (headers, timestamps, etc.)
    ├── sitemap.xml.cache         # Cached sitemap
    ├── sitemap.xml.meta.json     # Sitemap metadata
    └── sitemap.xml/              # Subdirectory for nested paths
        └── page1.xml.cache       # Nested sitemap entry
```

The `.cache` suffix ensures that URLs like `sitemap.xml` can coexist with nested URLs like `sitemap.xml/page1` without conflicts.

## Page

A `Page` dataclass is passed to callbacks. Key attributes include:

- `url`, `title`, `markdown`, `html`, `text`
- `metadata`, `fetched_at`, `status_code`, `content_hash`
- `depth`, `source`, `extraction_mode`
- `author`, `date`, `description`, `sitename`
- `from_cache`, `cache_path`, `headers`
- `previous_content_hash` - Hash of previously cached content (None if new)

Properties:

- `.domain`, `.is_seed`, `.is_from_sitemap`, `.is_discovered_link`, `.is_main_article`
- `.is_new` - True if page wasn't in cache before
- `.is_updated` - True if page was in cache but content changed
- `.is_unchanged` - True if page was in cache and content is identical
- `.is_new_or_updated` - True if page is either new or updated (most common check)

### Change Detection

The Page object provides built-in change detection to identify new or updated content:

```python
@crawler.on("page")
async def on_page(page: Page):
    if page.is_new:
        print(f"New page: {page.url}")
    elif page.is_updated:
        print(f"Updated page: {page.url}")
    elif page.is_unchanged:
        print(f"Unchanged page: {page.url}")

    # Most common pattern: process only new/updated
    if page.is_new_or_updated:
        process_changed_content(page)
```

**How it works:**

1. **With Last-Modified header**: Uses HTTP conditional GET (304 Not Modified)
   - Server indicates if content changed via 304 response
   - Most efficient - no content transfer if unchanged

2. **Without Last-Modified**: Falls back to content hash comparison
   - Compares SHA256 hash of current vs. previous content
   - Works even when server doesn't provide proper cache headers

3. **Status determination**:
   - `is_new = True` - Page not in cache before this crawl
   - `is_updated = True` - Page was cached, content hash changed
   - `is_unchanged = True` - Page was cached, content identical (304 or matching hash)

## Configuration Examples

### Basic crawl with redirects disabled

```toml
user_agent = "MyBot/1.0"
follow_redirects = false  # Don't follow redirects (default)
max_depth = 2
max_pages = 100

[cache]
dir = ".cache/mlcrawler"
mode = "conditional"  # Use conditional GET (default)
```

### Offline mode for rate-limited scenarios

```toml
user_agent = "MyBot/1.0"
follow_redirects = false

[cache]
mode = "offline"  # Only use cache, skip uncached URLs
dir = ".cache/mlcrawler"
```

### Aggressive caching with redirects

```toml
follow_redirects = true  # Follow redirects
max_depth = 3

[cache]
mode = "force"  # Never make HTTP requests, cache only
dir = ".cache/mlcrawler"
ttl = 86400  # 24 hours TTL for resources without validators
```

### Fresh fetch with cache updates

```toml
user_agent = "MyBot/1.0"

[cache]
mode = "bypass"  # Always fetch fresh, update cache
dir = ".cache/mlcrawler"
```

See the Examples page for practical code snippets and patterns.

---

_For a more verbose copy of the API docs (including full examples and best practices), see `API.md` in the repository root._
