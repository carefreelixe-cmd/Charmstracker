"""
Debug script to save HTML content for analysis
"""
import asyncio
import os
import time
from scrapers.james_avery_scraper import JamesAveryScraper

async def debug_save_html():
    print("Creating scraper instance...")
    scraper = JamesAveryScraper()
    
    try:
        print("\nFetching charms browse page...")
        async with scraper:
            await asyncio.sleep(1)  # Brief pause before request
            html = await scraper._make_request("https://www.jamesavery.com/charms")
            
            if html:
                print(f"\nReceived {len(html)} bytes of HTML")
                # Save the HTML content
                with open('charms_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("\nSaved HTML to charms_page.html")
            else:
                print("\n❌ Failed to get page content")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(debug_save_html())