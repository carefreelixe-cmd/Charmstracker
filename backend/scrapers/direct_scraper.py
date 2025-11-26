"""
Direct Web Scraper for Etsy, eBay, and Poshmark - IMPROVED VERSION
Uses actual HTML structure patterns from real pages
"""

import asyncio
import logging
from typing import List, Dict
import aiohttp
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class DirectMarketplaceScraper:
    """Direct scraper for marketplace charm listings - matches real HTML patterns"""
    
    def __init__(self):
        # Rotate user agents to avoid bot detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.current_ua_index = 0
    
    def get_headers(self, site=''):
        """Get realistic browser headers with rotating user agent"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return {
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
    
    async def scrape_etsy(self, search_query: str) -> List[Dict]:
        """
        Scrape Etsy marketplace
        Real pattern: <p class="wt-text-title-larger">₹ 463+</p>
        """
        try:
            url = f"https://www.etsy.com/in-en/market/{search_query.lower().replace(' ', '_')}"
            print(f"\n🎨 [ETSY] Scraping: {url}")
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.8)
            
            connector = aiohttp.TCPConnector(ssl=False)  # Bypass SSL verification
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.get_headers(), timeout=30) as response:
                    if response.status != 200:
                        print(f"❌ [ETSY] Status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    listings = []
                    
                    # Pattern 1: Look for wt-text-title-larger (price container)
                    price_elements = soup.find_all('p', class_=re.compile(r'wt-text-title-larger'))
                    print(f"🎨 [ETSY] Found {len(price_elements)} price elements")
                    
                    for price_elem in price_elements[:30]:
                        try:
                            # Get price text
                            price_text = price_elem.get_text(strip=True)
                            # Extract numbers (handles ₹, $, €, + symbol)
                            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                            if not price_match:
                                continue
                            
                            price = float(price_match.group())
                            
                            # Find parent container
                            parent = price_elem.find_parent('div', class_=re.compile(r'.*'))
                            if not parent:
                                parent = price_elem.find_parent('a')
                            
                            # Find link to listing
                            link_elem = parent.find('a', href=re.compile(r'/listing/')) if parent else None
                            if not link_elem:
                                # Try to find any link nearby
                                siblings = price_elem.find_previous_siblings('a') + price_elem.find_next_siblings('a')
                                for sib in siblings:
                                    if '/listing/' in str(sib.get('href', '')):
                                        link_elem = sib
                                        break
                            
                            url_val = ''
                            title = 'Etsy Charm Listing'
                            
                            if link_elem:
                                url_val = link_elem.get('href', '')
                                if url_val and not url_val.startswith('http'):
                                    url_val = f"https://www.etsy.com{url_val}"
                                
                                # Try to get title from link aria-label or text
                                title = link_elem.get('aria-label') or link_elem.get_text(strip=True) or title
                            
                            # Find image
                            img_elem = parent.find('img') if parent else None
                            image_url = None
                            if img_elem:
                                image_url = img_elem.get('src') or img_elem.get('data-src')
                            
                            listings.append({
                                'platform': 'etsy',
                                'title': title[:200],
                                'price': price,
                                'url': url_val,
                                'condition': 'New',
                                'seller': 'Etsy Seller',
                                'image_url': image_url
                            })
                            
                        except Exception as e:
                            print(f"⚠️ [ETSY] Parse error: {e}")
                            continue
                    
                    print(f"✅ [ETSY] Parsed {len(listings)} listings\n")
                    return listings
                    
        except Exception as e:
            print(f"❌ [ETSY] Scraping error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_ebay(self, search_query: str) -> List[Dict]:
        """
        Scrape eBay search results
        Real pattern: <div class="x-price-primary"><span class="ux-textspans">US $4.99</span></div>
        """
        try:
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&_sop=12"
            print(f"\n🛒 [EBAY] Scraping: {url}")
            
            # Small delay
            await asyncio.sleep(0.8)
            
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.get_headers(), timeout=30) as response:
                    if response.status != 200:
                        print(f"❌ [EBAY] Status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    listings = []
                    
                    # Pattern 1: Look for x-price-primary divs
                    price_divs = soup.find_all('div', class_='x-price-primary')
                    if not price_divs:
                        # Fallback: look for s-item__price
                        price_divs = soup.find_all('span', class_='s-item__price')
                    
                    print(f"🛒 [EBAY] Found {len(price_divs)} price divs")
                    
                    for price_div in price_divs[:30]:
                        try:
                            # Get price from ux-textspans or direct text
                            price_span = price_div.find('span', class_='ux-textspans')
                            price_text = price_span.get_text(strip=True) if price_span else price_div.get_text(strip=True)
                            
                            # Extract numeric price
                            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                            if not price_match:
                                continue
                            
                            price = float(price_match.group())
                            
                            # Find parent item container
                            item = price_div.find_parent('div', class_='s-item__info')
                            if not item:
                                item = price_div.find_parent('li', class_='s-item')
                            
                            title = 'eBay Charm Listing'
                            url_val = ''
                            condition = 'Used'
                            image_url = None
                            
                            if item:
                                # Find title
                                title_elem = item.find('div', class_='s-item__title')
                                if not title_elem:
                                    title_elem = item.find('h3', class_='s-item__title')
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                
                                # Skip ads
                                if 'shop on ebay' in title.lower() or 'shop now' in title.lower():
                                    continue
                                
                                # Find URL
                                link = item.find('a', class_='s-item__link')
                                if link:
                                    url_val = link.get('href', '')
                                
                                # Find condition
                                cond_elem = item.find('span', class_='SECONDARY_INFO')
                                if cond_elem:
                                    condition = cond_elem.get_text(strip=True)
                                
                                # Find image
                                img = item.find('img')
                                if img:
                                    image_url = img.get('src')
                            
                            listings.append({
                                'platform': 'ebay',
                                'title': title[:200],
                                'price': price,
                                'url': url_val,
                                'condition': condition,
                                'seller': 'eBay Seller',
                                'image_url': image_url
                            })
                            
                        except Exception as e:
                            print(f"⚠️ [EBAY] Parse error: {e}")
                            continue
                    
                    print(f"✅ [EBAY] Parsed {len(listings)} listings\n")
                    return listings
                    
        except Exception as e:
            print(f"❌ [EBAY] Scraping error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_poshmark(self, search_query: str) -> List[Dict]:
        """
        Scrape Poshmark search results
        Real pattern: <div class="listing__ipad-centered"><p class="h1"><span class="">$20</span></p></div>
        """
        try:
            url = f"https://poshmark.com/search?query={search_query.replace(' ', '%20')}"
            print(f"\n👗 [POSHMARK] Scraping: {url}")
            
            # Small delay
            await asyncio.sleep(0.8)
            
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.get_headers(), timeout=30) as response:
                    if response.status != 200:
                        print(f"❌ [POSHMARK] Status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    listings = []
                    
                    # Pattern 1: Look for listing__ipad-centered divs
                    centered_divs = soup.find_all('div', class_=re.compile(r'listing__.*centered'))
                    if not centered_divs:
                        # Fallback: look for any price h1
                        centered_divs = soup.find_all('p', class_='h1')
                    
                    print(f"👗 [POSHMARK] Found {len(centered_divs)} price containers")
                    
                    for div in centered_divs[:30]:
                        try:
                            # Find price - look for p.h1 > span
                            price_p = div.find('p', class_='h1') if div.name != 'p' else div
                            if not price_p:
                                continue
                            
                            price_span = price_p.find('span')
                            price_text = price_span.get_text(strip=True) if price_span else price_p.get_text(strip=True)
                            
                            # Extract numeric price
                            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                            if not price_match:
                                continue
                            
                            price = float(price_match.group())
                            
                            # Find parent tile/card
                            tile = div.find_parent('div', class_=re.compile(r'tile'))
                            if not tile:
                                tile = div.find_parent('a', href=re.compile(r'/listing/'))
                            
                            title = 'Poshmark Charm Listing'
                            url_val = ''
                            image_url = None
                            
                            if tile:
                                # Find link
                                link = tile if tile.name == 'a' else tile.find('a', href=re.compile(r'/listing/'))
                                if link:
                                    url_val = link.get('href', '')
                                    if url_val and not url_val.startswith('http'):
                                        url_val = f"https://poshmark.com{url_val}"
                                    
                                    # Get title from link title attribute or text
                                    title = link.get('title') or link.get_text(strip=True) or title
                                
                                # Find image
                                img = tile.find('img')
                                if img:
                                    image_url = img.get('src') or img.get('data-src')
                            
                            listings.append({
                                'platform': 'poshmark',
                                'title': title[:200],
                                'price': price,
                                'url': url_val,
                                'condition': 'Pre-owned',
                                'seller': 'Poshmark Seller',
                                'image_url': image_url
                            })
                            
                        except Exception as e:
                            print(f"⚠️ [POSHMARK] Parse error: {e}")
                            continue
                    
                    print(f"✅ [POSHMARK] Parsed {len(listings)} listings\n")
                    return listings
                    
        except Exception as e:
            print(f"❌ [POSHMARK] Scraping error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_all(self, charm_name: str) -> List[Dict]:
        """Scrape all three marketplaces concurrently"""
        print(f"\n{'='*60}")
        print(f"🔍 Starting direct scraping for: {charm_name}")
        print(f"{'='*60}\n")
        
        try:
            # Run all scrapers concurrently
            results = await asyncio.gather(
                self.scrape_etsy(charm_name),
                self.scrape_ebay(charm_name),
                self.scrape_poshmark(charm_name),
                return_exceptions=True
            )
            
            # Combine all results
            all_listings = []
            for result in results:
                if isinstance(result, list):
                    all_listings.extend(result)
                elif isinstance(result, Exception):
                    print(f"⚠️ Scraper error: {result}")
            
            print(f"\n{'='*60}")
            print(f"📊 TOTAL RESULTS: {len(all_listings)} listings")
            print(f"{'='*60}\n")
            
            return all_listings
            
        except Exception as e:
            print(f"❌ Error in scrape_all: {e}")
            import traceback
            traceback.print_exc()
            return []


# For testing
async def test_scraper():
    scraper = DirectMarketplaceScraper()
    results = await scraper.scrape_all("West Virginia charm")
    
    print(f"\n\n{'='*60}")
    print(f"FINAL RESULTS:")
    print(f"{'='*60}")
    for listing in results[:10]:
        print(f"\n{listing['platform'].upper()}: {listing['title']}")
        print(f"  💰 ${listing['price']}")
        print(f"  🔗 {listing['url'][:80]}")


if __name__ == '__main__':
    asyncio.run(test_scraper())
