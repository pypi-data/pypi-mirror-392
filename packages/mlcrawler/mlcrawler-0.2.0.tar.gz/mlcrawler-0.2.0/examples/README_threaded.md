# Threaded Processing Example

This example demonstrates how to use mlcrawler with multi-threaded processing using a queue.

## Features

- **Main Thread (Asyncio)**: Crawls website using sitemap
- **Callback Processing**: Removes unwanted HTML elements (`<svg>`, `<script>`, `<style>`) using BeautifulSoup
- **Queue-Based Architecture**: Passes processed pages to a background thread
- **Batch Processing**: Processes pages in batches of 10 OR every 5 seconds (whichever comes first)
- **Thread-Safe**: Uses `threading.Queue` for safe inter-thread communication

## How It Works

```
┌─────────────────┐
│  Main Thread    │
│   (asyncio)     │
│                 │
│  ┌──────────┐   │
│  │ Crawler  │   │
│  └────┬─────┘   │
│       │         │
│       ├─ on_page callback
│       │  - Parse with BeautifulSoup
│       │  - Remove <svg>, <script>, <style>
│       │  - Extract title
│       │  - Queue.put()
│       │         │
└───────┼─────────┘
        │
        ▼
  ┌──────────┐
  │  Queue   │
  └────┬─────┘
       │
       ▼
┌──────────────────┐
│ Worker Thread    │
│                  │
│  - Read from queue
│  - Batch items   │
│  - Process when: │
│    • 10 items OR │
│    • 5 seconds   │
│  - Print results │
└──────────────────┘
```

## Usage

```bash
cd /home/mludvig/src/crawler
uv run python examples/threaded_processing.py
```

## Code Structure

### PageProcessor Class

Handles background processing with configurable batch size and timeout:

```python
processor = PageProcessor(
    queue=page_queue,
    batch_size=10,      # Process every 10 documents
    timeout_seconds=5.0  # Or every 5 seconds
)
processor.start()
```

### Crawler Integration

```python
crawler = Crawler(
    user_agent="ThreadedExample/1.0",
    follow_redirects=False,
    max_pages=50,
    cache_mode="conditional",
)

@crawler.on("page")
async def on_page(page):
    # Parse and clean HTML
    soup = BeautifulSoup(page.html, 'lxml')
    for tag in soup.find_all(['svg', 'script', 'style']):
        tag.decompose()
    
    # Extract data
    cleaned_html = str(soup)
    title = page.title or soup.find('title').get_text()
    
    # Send to worker thread
    page_queue.put((page.url, title, cleaned_html))
```

## Example Output

```
Processing batch of 6 pages
📄 Using de-escalation to respond to risk
   URL: https://practice.example.com/page1
   HTML size: 54076 chars

📄 Finances and wills for tamariki
   URL: https://practice.example.com/page2
   HTML size: 23036 chars
...
```

## Why This Pattern?

1. **CPU-Intensive Work**: BeautifulSoup parsing can be CPU-intensive
2. **I/O Separation**: Keep async network I/O separate from CPU work
3. **Batch Efficiency**: Process multiple items together for better throughput
4. **Time-Based Flush**: Ensures low-latency processing even with low volume
5. **Backpressure**: Queue provides natural flow control

## Customization

### Adjust Batch Parameters

```python
processor = PageProcessor(
    queue=page_queue,
    batch_size=20,       # Larger batches
    timeout_seconds=10.0  # Less frequent processing
)
```

### Custom Processing

Replace the `_process_batch` method to:
- Save to database
- Generate embeddings
- Extract entities
- Index in search engine
- Send to message queue
- etc.

### Different Filtering

```python
# Remove different elements
for tag in soup.find_all(['nav', 'footer', '.ads', '#comments']):
    tag.decompose()
```

## Performance Notes

- Tested with 50 pages: 100% success rate
- All pages processed correctly
- Batching occurred at both size and time triggers
- Clean shutdown with no data loss

## Library Improvements Made

During development, we enhanced the library to:

1. **Added `follow_redirects` parameter** to Crawler API
2. **Added `cache_mode` parameter** for flexible caching strategies  
3. **Added `cache_ttl` parameter** for age-based cache control
4. **Added `close()` method** for explicit resource cleanup
5. **Fixed context manager** to properly call `close()`

These improvements make the library more flexible and easier to use in production scenarios.
