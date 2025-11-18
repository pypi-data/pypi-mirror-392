#!/usr/bin/env python3
"""Example: Multi-threaded processing with queue.

This script demonstrates how to:
1. Crawl a website in the main asyncio thread (using sitemap)
2. Process pages in a callback to remove unwanted elements
3. Send processed pages to a threading.Queue
4. Have a background thread process batches periodically

The processing thread handles batches every 5 seconds OR every 10 documents,
whichever comes first.
"""

import asyncio
import logging
import threading
import time
from pathlib import Path
from queue import Queue, Empty
from typing import Optional

from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PageProcessor:
    """Background thread that processes pages from a queue."""
    
    def __init__(self, queue: Queue, batch_size: int = 10, timeout_seconds: float = 5.0):
        """Initialize the processor.
        
        Args:
            queue: Queue to read pages from
            batch_size: Process batch when this many items accumulated
            timeout_seconds: Process batch after this many seconds even if not full
        """
        self.queue = queue
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.processed_count = 0
        
    def start(self):
        """Start the background processing thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("Processing thread started")
        
    def stop(self):
        """Stop the background processing thread."""
        self.running = False
        if self.thread:
            # Send sentinel to wake up thread
            self.queue.put(None)
            self.thread.join(timeout=10)
            logger.info(f"Processing thread stopped. Total processed: {self.processed_count}")
    
    def _process_loop(self):
        """Main processing loop running in background thread."""
        batch = []
        last_process_time = time.time()
        
        while self.running:
            try:
                # Calculate remaining timeout
                elapsed = time.time() - last_process_time
                remaining_timeout = max(0.1, self.timeout_seconds - elapsed)
                
                # Try to get an item with timeout
                item = self.queue.get(timeout=remaining_timeout)
                
                # Check for sentinel (None = stop signal)
                if item is None:
                    break
                
                batch.append(item)
                
                # Process batch if size reached OR timeout expired
                should_process = (
                    len(batch) >= self.batch_size or
                    (time.time() - last_process_time) >= self.timeout_seconds
                )
                
                if should_process:
                    self._process_batch(batch)
                    batch.clear()
                    last_process_time = time.time()
                    
            except Empty:
                # Timeout expired, process whatever we have
                if batch:
                    self._process_batch(batch)
                    batch.clear()
                last_process_time = time.time()
        
        # Process any remaining items
        if batch:
            self._process_batch(batch)
    
    def _process_batch(self, batch: list):
        """Process a batch of pages.
        
        Args:
            batch: List of (url, title, cleaned_html) tuples
        """
        logger.info(f"Processing batch of {len(batch)} pages")
        
        for url, title, cleaned_html in batch:
            # Simple processing: print URL and title
            print(f"📄 {title or 'Untitled'}")
            print(f"   URL: {url}")
            print(f"   HTML size: {len(cleaned_html)} chars")
            print()
            
            self.processed_count += 1
            
            # Here you could do more complex processing:
            # - Save to database
            # - Extract entities
            # - Generate embeddings
            # - Index in search engine
            # etc.


async def main():
    """Main function demonstrating the pattern."""
    
    # Import here to avoid issues if mlcrawler not installed
    try:
        from mlcrawler import Crawler
    except ImportError:
        # If running from source, add parent to path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.mlcrawler.api import Crawler
    
    # Create queue for passing pages between crawler and processor
    page_queue = Queue()
    
    # Start background processor thread
    processor = PageProcessor(
        queue=page_queue,
        batch_size=10,      # Process every 10 documents
        timeout_seconds=5.0  # Or every 5 seconds
    )
    processor.start()
    
    # Create crawler with sitemap mode
    crawler = Crawler(
        user_agent="ThreadedExample/1.0",
        follow_redirects=False,  # Don't follow redirects
        max_pages=50,  # Limit for demo
        cache_mode="conditional",  # Use conditional GET
    )
    
    # Statistics
    stats = {
        'crawled': 0,
        'processed': 0,
        'new': 0,
        'updated': 0,
        'unchanged': 0,
        'errors': 0,
    }
    
    # Define callback to process each page
    @crawler.on("page")
    async def on_page(page):
        """Process page with BeautifulSoup and add to queue."""
        try:
            stats['crawled'] += 1
            
            # Track page status
            if page.is_new:
                stats['new'] += 1
            elif page.is_updated:
                stats['updated'] += 1
            elif page.is_unchanged:
                stats['unchanged'] += 1
            
            # Only process new or updated pages
            if not page.is_new_or_updated:
                logger.debug(f"Skipping unchanged: {page.url}")
                return
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(page.html, 'lxml')
            
            # Remove unwanted elements
            for tag in soup.find_all(['svg', 'script', 'style']):
                tag.decompose()
            
            # Get cleaned HTML
            cleaned_html = str(soup)
            
            # Extract title (prefer page.title, fallback to soup)
            title = page.title
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
            
            # Add to queue for background processing
            page_queue.put((page.url, title, cleaned_html))
            stats['processed'] += 1
            
            logger.debug(f"Queued (new/updated): {page.url}")
            
        except Exception as e:
            logger.error(f"Error processing {page.url}: {e}")
            stats['errors'] += 1
    
    @crawler.on("error")
    async def on_error(url: str, error: Exception):
        """Handle errors."""
        logger.error(f"Failed to fetch {url}: {error}")
        stats['errors'] += 1
    
    @crawler.on("complete")
    async def on_complete(crawl_stats: dict):
        """Called when crawl completes."""
        logger.info(f"Crawl complete: {crawl_stats}")
    
    # Example: Crawl from sitemap
    sitemap_url = "https://practice.orangatamariki.govt.nz/sitemap.xml"
    
    logger.info(f"Starting crawl from sitemap: {sitemap_url}")
    
    try:
        # Crawl the sitemap
        pages = await crawler.crawl_sitemap(sitemap_url)
        
        logger.info(f"Crawl finished. Pages crawled: {len(pages)}")
        logger.info(f"Stats: {stats}")
        
        # Give processor time to finish processing queue
        logger.info("Waiting for processor to finish remaining items...")
        
        # Wait until queue is empty
        while not page_queue.empty():
            await asyncio.sleep(0.5)
        
        # Give one more timeout period for final batch
        await asyncio.sleep(processor.timeout_seconds + 1)
        
    finally:
        # Clean up
        processor.stop()
        await crawler.close()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Pages crawled: {stats['crawled']}")
    print(f"  - New: {stats['new']}")
    print(f"  - Updated: {stats['updated']}")
    print(f"  - Unchanged: {stats['unchanged']}")
    print(f"Pages processed (new/updated): {stats['processed']}")
    print(f"Pages in queue: {processor.processed_count}")
    print(f"Errors: {stats['errors']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
