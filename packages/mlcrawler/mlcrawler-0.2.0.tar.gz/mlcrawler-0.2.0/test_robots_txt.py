#!/usr/bin/env python3
"""
Test script for mlcrawler robots.txt compliance.

This script tests whether mlcrawler correctly respects robots.txt rules,
specifically checking if /Security/login paths are being excluded.

Usage:
    uv run python test_robots_txt.py

Expected behavior:
    - Crawler should respect obey_robots=True setting
    - URLs matching /Security/login* should be excluded
    - Script should report which URLs were crawled vs excluded
"""

import asyncio
from mlcrawler import Crawler


async def test_robots_compliance():
    """Test robots.txt compliance with practice.orangatamariki.govt.nz."""
    
    print("="*60)
    print("  Testing mlcrawler robots.txt Compliance")
    print("="*60)
    
    crawled_urls = []
    excluded_urls = []
    
    # Create crawler with robots.txt enforcement
    crawler = Crawler(
        max_depth=2,
        max_pages=50,
        same_domain_only=True,
        obey_robots=True,  # This should respect robots.txt
        concurrency=5,
        rate_limit_ms=500,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        follow_links=True,
        save_to_disk=False
    )
    
    @crawler.on("page")
    async def on_page(page):
        """Track crawled URLs."""
        crawled_urls.append(page.url)
        if "/Security/login" in page.url:
            print(f"WARNING: Crawled disallowed URL: {page.url}")
    
    @crawler.on("error")
    async def on_error(url, error):
        """Track errors."""
        print(f"ERROR fetching {url}: {error}")
    
    print("\nCrawling https://practice.orangatamariki.govt.nz/core-practice/advocacy")
    print("With obey_robots=True")
    print("\nExpected: /Security/login* URLs should be excluded")
    print("-"*60)
    
    try:
        await crawler.crawl(
            "https://practice.orangatamariki.govt.nz/core-practice/advocacy",
            follow_links=True
        )
    finally:
        await crawler.close()
    
    # Analyze results
    print("\n" + "="*60)
    print("  Results")
    print("="*60)
    
    security_login_urls = [url for url in crawled_urls if "/Security/login" in url]
    
    print(f"\nTotal URLs crawled: {len(crawled_urls)}")
    print(f"Security/login URLs found: {len(security_login_urls)}")
    
    if security_login_urls:
        print("\nWARNING: The following /Security/login URLs were crawled:")
        for url in security_login_urls:
            print(f"  - {url}")
        print("\nThis indicates mlcrawler is NOT respecting robots.txt!")
        print("\nExpected robots.txt rule:")
        print("  Disallow: /Security/*")
        return False
    else:
        print("\nSUCCESS: No /Security/login URLs were crawled")
        print("mlcrawler is correctly respecting robots.txt")
        return True


async def check_robots_txt():
    """Fetch and display robots.txt for the site."""
    import urllib.request
    
    print("\n" + "="*60)
    print("  Fetching robots.txt")
    print("="*60)
    
    url = "https://practice.orangatamariki.govt.nz/robots.txt"
    
    try:
        with urllib.request.urlopen(url) as response:
            robots_txt = response.read().decode('utf-8')
            print(f"\nContent from {url}:\n")
            print(robots_txt)
    except Exception as e:
        print(f"\nFailed to fetch robots.txt: {e}")


async def main():
    """Run all tests."""
    # First, show robots.txt
    await check_robots_txt()
    
    # Then test compliance
    success = await test_robots_compliance()
    
    # Summary
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    
    if success:
        print("\nmlcrawler is working correctly with robots.txt")
    else:
        print("\nISSUE FOUND: mlcrawler is NOT respecting robots.txt")
        print("\nRecommended fix in mlcrawler:")
        print("  1. Check RobotFileParser implementation")
        print("  2. Ensure robots.txt is fetched before crawling")
        print("  3. Verify URL filtering before adding to queue")
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
