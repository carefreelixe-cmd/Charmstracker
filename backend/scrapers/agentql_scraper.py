"""
AgentQL Scraper - AI-powered web scraping that bypasses bot detection
Uses natural language queries to extract data from marketplace pages
"""
import agentql
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import time

load_dotenv()

class AgentQLMarketplaceScraper:
    def __init__(self, headless=True):
        self.api_key = os.getenv('AGENTQL_API_KEY')
        if not self.api_key:
            raise ValueError("❌ AGENTQL_API_KEY not found in .env file")
        
        self.headless = headless
        print(f"🤖 [AGENTQL] Initialized with API key: {self.api_key[:20]}... (headless={headless})")
    
    def scrape_etsy(self, charm_name):
        """Scrape Etsy using AgentQL's AI-powered queries"""
        print(f"🎨 [ETSY-AGENTQL] Scraping Etsy for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                # Launch browser with stealth settings
                browser = playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # Wrap page with AgentQL
                page = agentql.wrap(context.new_page())
                
                # Navigate to Etsy search
                url = f"https://www.etsy.com/search?q={charm_name.replace(' ', '+')}"
                print(f"🔗 [ETSY] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                # Wait a bit for JavaScript to render
                time.sleep(4)
                
                # Take screenshot for debugging (only if visible)
                if not self.headless:
                    page.screenshot(path="etsy_agentql_debug.png")
                    print("📸 [ETSY] Screenshot saved")
                
                # Try Etsy-specific query first
                ETSY_QUERY = """
                {
                    search_results[] {
                        listing_title
                        listing_price
                        price_currency
                        currency_symbol
                        listing_url
                        listing_image
                    }
                }
                """
                
                print("🔍 [ETSY] Querying page with Etsy-specific selectors...")
                response = page.query_data(ETSY_QUERY)
                
                # If first query fails, try generic query
                if not response or 'search_results' not in response or not response.get('search_results'):
                    print("⚠️ [ETSY] First query failed, trying generic selectors...")
                    GENERIC_QUERY = """
                    {
                        products[] {
                            title
                            price
                            currency
                            link
                            image
                        }
                    }
                    """
                    response = page.query_data(GENERIC_QUERY)
                
                # Check which field structure we got back
                products = []
                if response and 'search_results' in response:
                    products = response['search_results']
                    field_map = {'title': 'listing_title', 'price': 'listing_price', 'link': 'listing_url', 'image': 'listing_image'}
                elif response and 'products' in response:
                    products = response['products']
                    field_map = {'title': 'title', 'price': 'price', 'link': 'link', 'image': 'image'}
                else:
                    print("⚠️ [ETSY] No products found in response")
                    print(f"Response keys: {list(response.keys()) if response else 'None'}")
                    browser.close()
                    return []
                
                print(f"✅ [ETSY] Found {len(products)} products")
                
                # Convert to our format
                listings = []
                for product in products[:10]:  # Limit to 10 results
                    try:
                        # Get fields using the detected field map
                        title = product.get(field_map['title']) or product.get('title', '')
                        price_str = str(product.get(field_map['price']) or product.get('price', '0'))
                        url = product.get(field_map['link']) or product.get('link', '')
                        image = product.get(field_map['image']) or product.get('image', '')
                        
                        # Get currency info from page
                        currency_symbol = product.get('currency_symbol', '')
                        currency_code = product.get('price_currency') or product.get('currency', '')
                        
                        # Detect currency from price string or symbol
                        import re
                        detected_currency = 'USD'  # default
                        
                        if '₹' in price_str or '₹' in currency_symbol or 'INR' in str(currency_code).upper():
                            detected_currency = 'INR'
                        elif '€' in price_str or '€' in currency_symbol or 'EUR' in str(currency_code).upper():
                            detected_currency = 'EUR'
                        elif '£' in price_str or '£' in currency_symbol or 'GBP' in str(currency_code).upper():
                            detected_currency = 'GBP'
                        elif '$' in price_str or '$' in currency_symbol or 'USD' in str(currency_code).upper():
                            detected_currency = 'USD'
                        
                        # Extract numeric price (NO CONVERSION - store as shown)
                        price = 0
                        # Extract just the number, keep as-is
                        price_match = re.search(r'([\d,]+\.?\d*)', price_str.replace(',', ''))
                        if price_match:
                            try:
                                price = float(price_match.group(1))
                            except:
                                price = 0
                        
                        # Validate price exists
                        if not title or not price or price <= 0:
                            print(f"  ⚠️ Skipping: title={bool(title)}, price={price}")
                            continue
                        
                        listing = {
                            'platform': 'Etsy',
                            'title': title,
                            'price': price,
                            'currency': detected_currency,
                            'url': url,
                            'image_url': image,
                            'condition': 'New'
                        }
                        listings.append(listing)
                        
                        # Display with correct currency symbol
                        curr_symbol = {'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£'}.get(detected_currency, '$')
                        print(f"  💎 {listing['title'][:50]}... - {curr_symbol}{listing['price']} {detected_currency}")
                    except Exception as e:
                        print(f"  ⚠️ Error parsing product: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                context.close()
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [ETSY] AgentQL error: {e}")
                import traceback
                traceback.print_exc()
                return []
    
    def scrape_ebay(self, charm_name):
        """Scrape eBay using AgentQL's AI-powered queries"""
        print(f"🛒 [EBAY-AGENTQL] Scraping eBay for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = agentql.wrap(context.new_page())
                
                url = f"https://www.ebay.com/sch/i.html?_nkw={charm_name.replace(' ', '+')}&_sop=12"
                print(f"🔗 [EBAY] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                time.sleep(3)
                
                if not self.headless:
                    page.screenshot(path="ebay_agentql_debug.png")
                    print("📸 [EBAY] Screenshot saved")
                
                # Check for bot detection
                html = page.content()
                if 'interrupt' in html.lower() or 'captcha' in html.lower() or 'challenge' in html.lower():
                    print("❌ [EBAY] Bot detection triggered even with AgentQL")
                    context.close()
                    browser.close()
                    return []
                
                QUERY = """
                {
                    items[] {
                        title
                        price
                        shipping
                        condition
                        url
                        image
                    }
                }
                """
                
                print("🔍 [EBAY] Querying page with AgentQL...")
                response = page.query_data(QUERY)
                
                if not response or 'items' not in response:
                    print("⚠️ [EBAY] No items found in response")
                    context.close()
                    browser.close()
                    return []
                
                items = response['items']
                print(f"✅ [EBAY] Found {len(items)} items")
                
                listings = []
                for item in items[:10]:
                    try:
                        price_str = str(item.get('price', '0'))
                        price = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
                        
                        listing = {
                            'platform': 'eBay',
                            'title': item.get('title', ''),
                            'price': price,
                            'currency': 'USD',
                            'url': item.get('url', ''),
                            'image_url': item.get('image', ''),
                            'condition': item.get('condition', 'Used')
                        }
                        listings.append(listing)
                        print(f"  🛒 {listing['title'][:50]}... - ${listing['price']}")
                    except Exception as e:
                        print(f"  ⚠️ Error parsing item: {e}")
                        continue
                
                context.close()
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [EBAY] AgentQL error: {e}")
                import traceback
                traceback.print_exc()
                return []
    
    def scrape_poshmark(self, charm_name):
        """Scrape Poshmark using AgentQL's AI-powered queries"""
        print(f"👗 [POSHMARK-AGENTQL] Scraping Poshmark for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = agentql.wrap(context.new_page())
                
                url = f"https://poshmark.com/search?query={charm_name.replace(' ', '+')}"
                print(f"🔗 [POSHMARK] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                time.sleep(3)
                
                if not self.headless:
                    page.screenshot(path="poshmark_agentql_debug.png")
                    print("📸 [POSHMARK] Screenshot saved")
                
                QUERY = """
                {
                    listings[] {
                        title
                        price
                        brand
                        size
                        url
                        image
                    }
                }
                """
                
                print("🔍 [POSHMARK] Querying page with AgentQL...")
                response = page.query_data(QUERY)
                
                if not response or 'listings' not in response:
                    print("⚠️ [POSHMARK] No listings found in response")
                    context.close()
                    browser.close()
                    return []
                
                listings_data = response['listings']
                print(f"✅ [POSHMARK] Found {len(listings_data)} listings")
                
                listings = []
                for listing in listings_data[:10]:
                    try:
                        price_str = str(listing.get('price', '0'))
                        price = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
                        
                        result = {
                            'platform': 'Poshmark',
                            'title': listing.get('title', ''),
                            'price': price,
                            'currency': 'USD',
                            'url': listing.get('url', ''),
                            'image_url': listing.get('image', ''),
                            'condition': 'Pre-owned'
                        }
                        listings.append(result)
                        print(f"  👗 {result['title'][:50]}... - ${result['price']}")
                    except Exception as e:
                        print(f"  ⚠️ Error parsing listing: {e}")
                        continue
                
                context.close()
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [POSHMARK] AgentQL error: {e}")
                import traceback
                traceback.print_exc()
                return []
    
    def scrape_all(self, charm_name):
        """Scrape all marketplaces with AgentQL"""
        print(f"\n🤖 [AGENTQL] Starting AI-powered scraping for: {charm_name}\n")
        
        all_listings = []
        
        # Scrape Etsy
        etsy_listings = self.scrape_etsy(charm_name)
        all_listings.extend(etsy_listings)
        print(f"\n✅ [ETSY] Collected {len(etsy_listings)} listings\n")
        
        # Scrape eBay
        ebay_listings = self.scrape_ebay(charm_name)
        all_listings.extend(ebay_listings)
        print(f"\n✅ [EBAY] Collected {len(ebay_listings)} listings\n")
        
        # Scrape Poshmark
        poshmark_listings = self.scrape_poshmark(charm_name)
        all_listings.extend(poshmark_listings)
        print(f"\n✅ [POSHMARK] Collected {len(poshmark_listings)} listings\n")
        
        print(f"\n📊 [AGENTQL] TOTAL: {len(all_listings)} listings from all platforms\n")
        return all_listings


def test_agentql_scraper():
    """Test the AgentQL scraper"""
    print("🧪 Testing AgentQL Scraper...\n")
    
    # Use headless=False for testing so you can see browsers
    scraper = AgentQLMarketplaceScraper(headless=False)
    results = scraper.scrape_all("West Virginia charm")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {len(results)} total listings")
    print(f"{'='*60}\n")
    
    for listing in results:
        print(f"  {listing['platform']}: {listing['title'][:60]}... - ${listing['price']}")
    
    return results


if __name__ == "__main__":
    test_agentql_scraper()
