"""
Test script for James Avery scraper functionality
"""

import asyncio
import logging
from scrapers.james_avery_scraper import test_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run scraper tests"""
    try:
        await test_scraper()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())