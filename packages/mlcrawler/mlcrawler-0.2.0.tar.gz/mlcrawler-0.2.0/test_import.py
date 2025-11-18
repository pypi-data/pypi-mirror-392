"""Quick test to verify mlcrawler can be imported and used as a library."""

import asyncio
from mlcrawler import Crawler, Page


async def test_import():
    """Test that we can import and instantiate the library."""
    print("✓ Import successful")
    
    # Test instantiation
    crawler = Crawler(max_pages=1)
    print(f"✓ Crawler created: {crawler}")
    
    # Test we have the right attributes
    assert hasattr(crawler, 'crawl')
    assert hasattr(crawler, 'crawl_sitemap')
    assert hasattr(crawler, 'stream')
    print("✓ Crawler has expected methods")
    
    # Test Page class
    page = Page(
        url="https://example.com",
        title="Test",
        markdown="# Test",
        html="<h1>Test</h1>",
        text="Test",
    )
    assert page.url == "https://example.com"
    assert page.is_seed
    print("✓ Page class works")
    
    print("\n✅ All import tests passed!")


if __name__ == "__main__":
    asyncio.run(test_import())
