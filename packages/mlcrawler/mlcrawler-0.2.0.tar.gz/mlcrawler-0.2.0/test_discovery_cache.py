#!/usr/bin/env python3
"""Test the discovery cache optimization in seed mode."""

import asyncio
import logging
from pathlib import Path
import tempfile
from mlcrawler import Crawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test discovery cache with seed mode."""
    
    # First crawl - everything will be new
    print("\n" + "="*80)
    print("FIRST CRAWL - Everything should be new")
    print("="*80 + "\n")
    
    crawler = Crawler(
        cache_dir=".cache/test_discovery_cache",
        output_dir="test_discovery_cache",
        follow_links=False,
    )
    
    pages = await crawler.crawl("https://httpbin.org/html")
    new_count = sum(1 for p in pages if p.is_new)
    
    for page in pages:
        if page.is_new:
            print(f"✓ NEW: {page.url}")
    
    await crawler.close()
    print(f"\nFirst crawl: {new_count} new pages")
    
    # Second crawl - everything should be unchanged, using discovery cache
    print("\n" + "="*80)
    print("SECOND CRAWL - Should use discovery cache for unchanged pages")
    print("="*80 + "\n")
    
    crawler2 = Crawler(
        cache_dir=".cache/test_discovery_cache",
        output_dir="test_discovery_cache",
        follow_links=False,
    )
    
    pages2 = await crawler2.crawl("https://httpbin.org/html")
    unchanged_count = sum(1 for p in pages2 if p.is_unchanged)
    
    for page in pages2:
        if page.is_unchanged:
            print(f"○ UNCHANGED: {page.url}")
    
    await crawler2.close()
    print(f"\nSecond crawl: {unchanged_count} unchanged pages")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ First crawl: {new_count} new pages")
    print(f"○ Second crawl: {unchanged_count} unchanged pages")
    print("\nCheck the logs above for 'Discovery cache' statistics!")
    print("Expected: ~100% cache hit rate on second crawl")

if __name__ == "__main__":
    asyncio.run(main())
