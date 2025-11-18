#!/usr/bin/env python3
"""Test the threaded processing example with a small sitemap."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Run the example with modified settings
async def test_run():
    # Import the script functions
    from examples.threaded_processing import main as threaded_main
    
    await threaded_main()

if __name__ == "__main__":
    asyncio.run(test_run())
