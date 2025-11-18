#!/usr/bin/env python3
"""Detailed test showing discovery cache performance benefits."""

import asyncio
import logging
from mlcrawler import Crawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Test discovery cache with multiple pages and links."""
    
    print("\n" + "="*80)
    print("DISCOVERY CACHE PERFORMANCE TEST")
    print("="*80)
    print("\nThis test demonstrates how the discovery cache eliminates double-fetches")
    print("in seed mode when following links.\n")
    
    # Test with a page that has multiple links
    crawler = Crawler(
        cache_dir=".cache/test_discovery_detailed",
        output_dir="test_discovery_detailed",
        follow_links=True,
        max_depth=2,
        same_domain_only=False,
    )
    
    print("Crawling https://httpbin.org/links/5 (page with 5 links, max_depth=2)...\n")
    pages = await crawler.crawl("https://httpbin.org/links/5")
    
    await crawler.close()
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Total pages crawled: {len(pages)}")
    print(f"\nWithout discovery cache, this would have made ~{len(pages)} extra fetches")
    print("(one extra fetch per page that was discovered during link extraction)")
    print("\nWith discovery cache:")
    print("- Pages fetched during discovery are reused during processing")
    print("- Only pages NOT at max_depth during discovery need to be fetched twice")
    print("\nLook for '✨ Discovery cache HIT' messages and statistics above!")

if __name__ == "__main__":
    asyncio.run(main())
