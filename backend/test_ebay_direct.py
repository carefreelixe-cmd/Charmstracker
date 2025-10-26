"""
Test direct eBay web scraping
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def test_ebay_search():
    print("=" * 80)
    print("🧪 TESTING EBAY WEB SCRAPING")
    print("=" * 80)
    print()
    
    # Test search for "pandora bow charm" (like your link)
    search_query = "James Avery bow charm"
    url = "https://www.ebay.com/sch/i.html"
    
    params = {
        '_nkw': search_query,
        '_sacat': '0',
        'LH_Sold': '0',  # Active listings
        '_udlo': '10',   # Min $10
        '_udhi': '500',  # Max $500
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f"🔍 Searching eBay for: {search_query}")
    print(f"📡 URL: {url}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"📊 Response Status: {response.status}")
                print(f"📝 Content Type: {response.headers.get('Content-Type', 'Unknown')}")
                print()
                
                if response.status == 200:
                    html = await response.text()
                    print(f"📄 HTML Length: {len(html)} characters")
                    print()
                    
                    # Parse HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all items
                    items = soup.find_all('li', class_='s-item')
                    print(f"🎯 Found {len(items)} potential items")
                    print()
                    
                    if items:
                        print("📦 FIRST 5 LISTINGS:")
                        print("-" * 80)
                        
                        count = 0
                        for idx, item in enumerate(items[:10], 1):
                            try:
                                # Skip promoted items
                                if item.find('span', class_='PROMOTED'):
                                    continue
                                
                                # Extract title
                                title_elem = item.find('div', class_='s-item__title')
                                if not title_elem:
                                    title_elem = item.find('h3', class_='s-item__title')
                                
                                title = title_elem.text.strip() if title_elem else 'No title'
                                
                                # Extract price
                                price_elem = item.find('span', class_='s-item__price')
                                price_text = price_elem.text.strip() if price_elem else 'No price'
                                
                                # Extract price value
                                price_match = re.search(r'\$([\d,]+\.?\d*)', price_text)
                                price_value = float(price_match.group(1).replace(',', '')) if price_match else 0
                                
                                # Extract URL
                                link_elem = item.find('a', class_='s-item__link')
                                url = link_elem.get('href', '') if link_elem else ''
                                
                                # Extract condition
                                condition_elem = item.find('span', class_='SECONDARY_INFO')
                                condition = condition_elem.text.strip() if condition_elem else 'Used'
                                
                                # Extract image
                                img_elem = item.find('img', class_='s-item__image-img')
                                image_url = img_elem.get('src', '') if img_elem else ''
                                
                                if price_value > 0:
                                    count += 1
                                    print(f"\n{count}. {title[:70]}")
                                    print(f"   💵 Price: ${price_value:.2f}")
                                    print(f"   📦 Condition: {condition}")
                                    print(f"   🔗 URL: {url[:80]}...")
                                    print(f"   🖼️  Image: {image_url[:80]}...")
                                    
                                    if count >= 5:
                                        break
                                
                            except Exception as e:
                                print(f"   ⚠️  Error parsing item {idx}: {str(e)}")
                                continue
                        
                        print()
                        print("=" * 80)
                        print(f"✅ SUCCESS! Found {count} valid listings")
                        print("=" * 80)
                    else:
                        print("❌ No items found in HTML")
                        print("\n📝 Sample HTML (first 1000 chars):")
                        print(html[:1000])
                else:
                    print(f"❌ Failed to fetch page: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ebay_search())
