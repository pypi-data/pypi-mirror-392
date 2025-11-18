#!/usr/bin/env python3
"""
Test script to reproduce sitemap cache path bug in mlcrawler.

PROBLEM:
  When crawling a sitemap index (sitemap that contains other sitemaps),
  mlcrawler creates cache path like:
    .cache/mlcrawler/example.com/sitemap.xml              <- file
    .cache/mlcrawler/example.com/sitemap.xml/sub/...     <- tries to mkdir under file!
  
  Error: [Errno 20] Not a directory

EXPECTED:
  Cache paths should be:
    .cache/mlcrawler/example.com/sitemap.xml              <- file
    .cache/mlcrawler/example.com/sitemap.xml~sub~...     <- separate file

URL EXAMPLES:
  https://practice.orangatamariki.govt.nz/sitemap.xml
  https://practice.orangatamariki.govt.nz/sitemap.xml/sitemap/SilverStripe-CMS-Model-SiteTree/1

HOW TO FIX (in mlcrawler):
  1. Find cache path generation code
  2. Replace '/' with '~' or similar in URL paths to avoid directory conflicts
  3. Or create hash-based cache keys instead of URL-based paths
"""

import asyncio
from pathlib import Path
from mlcrawler import Crawler


async def test_sitemap_crawl():
    """Test sitemap crawling that triggers the cache path bug."""
    
    print("Testing sitemap crawl with cache...")
    print("="*60)
    print("\nExpected bug:")
    print("  Sitemap index creates .cache/.../sitemap.xml as file")
    print("  Then nested sitemap tries to create .cache/.../sitemap.xml/sub/...")
    print("  Result: [Errno 20] Not a directory\n")
    
    # Clean up old cache to ensure fresh test
    cache_dir = Path('.cache/mlcrawler/practice.orangatamariki.govt.nz')
    if cache_dir.exists():
        print(f"🧹 Cleaning cache: {cache_dir}\n")
        import shutil
        shutil.rmtree(cache_dir, ignore_errors=True)
    
    # This sitemap has a sitemap index with nested sitemaps
    sitemap_url = "https://practice.orangatamariki.govt.nz/sitemap.xml"
    
    crawler = Crawler(
        max_pages=3,
        save_to_disk=False,
    )
    
    pages = []
    
    async def collect_page(page):
        pages.append(page)
        print(f"✅ Collected: {page.url}")
    
    try:
        print(f"Crawling sitemap: {sitemap_url}\n")
        await crawler.crawl_sitemap(sitemap_url, callback=collect_page)
        
        print(f"\n✅ Success! Collected {len(pages)} pages")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis is the bug! Fix it in mlcrawler/cache.py")
        print("by using URL-safe cache keys (replace '/' with '~' etc)")


if __name__ == '__main__':
    asyncio.run(test_sitemap_crawl())
