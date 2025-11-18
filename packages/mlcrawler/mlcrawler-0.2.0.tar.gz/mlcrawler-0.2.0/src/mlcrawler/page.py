"""Page dataclass representing a crawled web page with all its data."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Page:
    """Represents a crawled web page with all extracted data and metadata.

    This is the primary data structure passed to user callbacks when pages
    are crawled. It contains the original HTML, extracted markdown, metadata,
    and crawl context.

    Attributes:
        url: Original URL of the page
        title: Extracted page title
        markdown: Content converted to Markdown format
        html: Original HTML content
        text: Plain text content (no markup)

        metadata: Complete metadata dictionary
        fetched_at: Timestamp when page was fetched
        status_code: HTTP status code
        content_hash: SHA256 hash of content

        depth: Crawl depth (0 for seed URLs)
        source: How URL was discovered ("seed", "sitemap", or "link")
        extraction_mode: Extraction method used ("article" or "fullpage")

        author: Optional author from trafilatura metadata
        date: Optional publish date from trafilatura metadata
        description: Optional description from trafilatura metadata
        sitename: Optional site name from trafilatura metadata

        from_cache: Whether content was served from cache
        cache_path: Path to cached content file
        headers: HTTP response headers
    """

    # Core content
    url: str
    title: str
    markdown: str
    html: str
    text: str

    # Metadata
    metadata: dict = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=datetime.now)
    status_code: int = 200
    content_hash: str = ""

    # Crawl context
    depth: int = 0
    source: str = "seed"  # "seed", "sitemap", or "link"
    extraction_mode: str = "fullpage"  # "article" or "fullpage"

    # Optional trafilatura metadata
    author: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    sitename: Optional[str] = None

    # Cache information
    from_cache: bool = False
    cache_path: Optional[Path] = None
    headers: dict = field(default_factory=dict)
    previous_content_hash: Optional[str] = None  # Hash of previously cached content

    def __str__(self) -> str:
        """String representation showing key information."""
        return f"Page(url={self.url!r}, title={self.title!r}, depth={self.depth})"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Page(url={self.url!r}, title={self.title!r}, "
            f"markdown_len={len(self.markdown)}, depth={self.depth}, "
            f"source={self.source!r}, from_cache={self.from_cache})"
        )

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        return urlparse(self.url).netloc

    @property
    def is_seed(self) -> bool:
        """Check if this was a seed URL."""
        return self.source == "seed"

    @property
    def is_from_sitemap(self) -> bool:
        """Check if this came from a sitemap."""
        return self.source == "sitemap"

    @property
    def is_discovered_link(self) -> bool:
        """Check if this was discovered by following links."""
        return self.source == "link"

    @property
    def is_main_article(self) -> bool:
        """Check if this was extracted as main article content."""
        return self.extraction_mode == "article"

    @property
    def is_new(self) -> bool:
        """Check if this is a new page (not previously cached).

        Returns:
            True if the page wasn't in cache before this fetch
        """
        return self.previous_content_hash is None

    @property
    def is_updated(self) -> bool:
        """Check if this page was updated since last cache.

        Returns:
            True if page was in cache but content changed
        """
        return (
            self.previous_content_hash is not None
            and self.content_hash != self.previous_content_hash
        )

    @property
    def is_unchanged(self) -> bool:
        """Check if this page is unchanged from cache.

        Returns:
            True if page was in cache and content is identical
        """
        return (
            self.previous_content_hash is not None
            and self.content_hash == self.previous_content_hash
        )

    @property
    def is_new_or_updated(self) -> bool:
        """Check if this page is either new or updated.

        This is the most common check - whether the page has changed
        and needs processing.

        Returns:
            True if page is new or content changed
        """
        return self.is_new or self.is_updated

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary containing all page data
        """
        return {
            "url": self.url,
            "title": self.title,
            "markdown": self.markdown,
            "html": self.html,
            "text": self.text,
            "metadata": self.metadata,
            "fetched_at": self.fetched_at.isoformat(),
            "status_code": self.status_code,
            "content_hash": self.content_hash,
            "depth": self.depth,
            "source": self.source,
            "extraction_mode": self.extraction_mode,
            "author": self.author,
            "date": self.date,
            "description": self.description,
            "sitename": self.sitename,
            "from_cache": self.from_cache,
            "cache_path": str(self.cache_path) if self.cache_path else None,
            "headers": self.headers,
            "previous_content_hash": self.previous_content_hash,
            "is_new": self.is_new,
            "is_updated": self.is_updated,
            "is_unchanged": self.is_unchanged,
        }
