#!/usr/bin/env python3
"""Test the discovery cache optimization with link following."""

import asyncio
import logging
from mlcrawler import Crawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test discovery cache with link following."""
    
    # First crawl - everything will be new
    print("\n" + "="*80)
    print("FIRST CRAWL - Discovering and processing links")
    print("="*80 + "\n")
    
    crawler = Crawler(
        cache_dir=".cache/test_discovery_cache_links",
        output_dir="test_discovery_cache_links",
        follow_links=True,
        max_depth=2,  # Follow two levels of links so discovery fetches depth-1 pages
        same_domain_only=False,  # Allow following to different domains for this test
    )
    
    pages = await crawler.crawl("https://httpbin.org/links/3")  # Page with 3 links
    new_count = sum(1 for p in pages if p.is_new)
    
    print(f"\nFirst crawl processed {len(pages)} pages:")
    for page in pages:
        status = "✓ NEW" if page.is_new else "○ UNCHANGED"
        print(f"{status}: {page.url}")
    
    await crawler.close()
    
    # Second crawl - everything should be unchanged, discovery cache should be used
    print("\n" + "="*80)
    print("SECOND CRAWL - Should use discovery cache for unchanged pages")
    print("="*80 + "\n")
    
    crawler2 = Crawler(
        cache_dir=".cache/test_discovery_cache_links",
        output_dir="test_discovery_cache_links",
        follow_links=True,
        max_depth=2,
        same_domain_only=False,
    )
    
    pages2 = await crawler2.crawl("https://httpbin.org/links/3")
    unchanged_count = sum(1 for p in pages2 if p.is_unchanged)
    
    print(f"\nSecond crawl processed {len(pages2)} pages:")
    for page in pages2:
        status = "○ UNCHANGED" if page.is_unchanged else "✓ NEW/UPDATED"
        print(f"{status}: {page.url}")
    
    await crawler2.close()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ First crawl: {new_count} new pages")
    print(f"○ Second crawl: {unchanged_count} unchanged pages")
    print("\nLook for 'Discovery cache' statistics in the logs above!")
    print("The discovery cache eliminates the double-fetch for unchanged pages.")

if __name__ == "__main__":
    asyncio.run(main())
