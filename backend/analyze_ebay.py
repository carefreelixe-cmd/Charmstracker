"""
Analyze eBay HTML structure
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def analyze_ebay_html():
    url = "https://www.ebay.com/sch/i.html"
    params = {'_nkw': 'James Avery bow charm'}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("=" * 80)
            print("ANALYZING EBAY HTML STRUCTURE")
            print("=" * 80)
            print()
            
            # Try different selectors
            print("🔍 Looking for different item containers...")
            print()
            
            # Method 1: s-item
            items_1 = soup.find_all('li', class_='s-item')
            print(f"1. li.s-item: {len(items_1)} found")
            
            # Method 2: srp-results
            items_2 = soup.find_all('div', class_='s-item')
            print(f"2. div.s-item: {len(items_2)} found")
            
            # Method 3: Look for srp-river
            river = soup.find('ul', class_='srp-results')
            if river:
                print(f"3. ul.srp-results: FOUND!")
                items_3 = river.find_all('li')
                print(f"   Contains {len(items_3)} <li> elements")
            else:
                print(f"3. ul.srp-results: NOT FOUND")
            
            # Method 4: Look for any list items
            all_lis = soup.find_all('li', limit=20)
            print(f"4. Total <li> elements (first 20): {len(all_lis)}")
            
            print()
            print("=" * 80)
            print("SAMPLE LIST ITEMS:")
            print("=" * 80)
            
            for idx, li in enumerate(all_lis[:5], 1):
                print(f"\n{idx}. Classes: {li.get('class', [])}")
                print(f"   Has title: {'s-item__title' in str(li)}")
                print(f"   Has price: {'s-item__price' in str(li)}")
                print(f"   Text preview: {li.text[:100].strip()}")

if __name__ == "__main__":
    asyncio.run(analyze_ebay_html())
