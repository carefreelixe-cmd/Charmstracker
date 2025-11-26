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
    def __init__(self):
        self.api_key = os.getenv('AGENTQL_API_KEY')
        if not self.api_key:
            raise ValueError("❌ AGENTQL_API_KEY not found in .env file")
        
        print(f"🤖 [AGENTQL] Initialized with API key: {self.api_key[:20]}...")
    
    def scrape_etsy(self, charm_name):
        """Scrape Etsy using AgentQL's AI-powered queries"""
        print(f"🎨 [ETSY-AGENTQL] Scraping Etsy for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                # Launch persistent browser with Chrome profile (looks more human-like)
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(os.getcwd(), "playwright_data"),
                    channel="chrome" if os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") else None,
                    headless=False,  # Visible browser for debugging
                    no_viewport=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                # Wrap page with AgentQL
                page = agentql.wrap(browser.new_page())
                
                # Navigate to Etsy search
                url = f"https://www.etsy.com/search?q={charm_name.replace(' ', '+')}"
                print(f"🔗 [ETSY] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                # Wait a bit for JavaScript to render
                time.sleep(3)
                
                # Take screenshot for debugging
                page.screenshot(path="etsy_agentql_debug.png")
                print("📸 [ETSY] Screenshot saved")
                
                # Use natural language query to find products
                QUERY = """
                {
                    products[] {
                        title
                        price
                        link
                        image
                    }
                }
                """
                
                print("🔍 [ETSY] Querying page with AgentQL...")
                response = page.query_data(QUERY)
                
                if not response or 'products' not in response:
                    print("⚠️ [ETSY] No products found in response")
                    browser.close()
                    return []
                
                products = response['products']
                print(f"✅ [ETSY] Found {len(products)} products")
                
                # Convert to our format
                listings = []
                for product in products[:10]:  # Limit to 10 results
                    try:
                        # Extract price (remove currency symbols)
                        price_str = str(product.get('price', '0'))
                        price = float(''.join(c for c in price_str if c.isdigit() or c == '.'))
                        
                        listing = {
                            'platform': 'Etsy',
                            'title': product.get('title', ''),
                            'price': price,
                            'currency': 'USD',
                            'url': product.get('link', ''),
                            'image_url': product.get('image', ''),
                            'condition': 'New'
                        }
                        listings.append(listing)
                        print(f"  💎 {listing['title'][:50]}... - ${listing['price']}")
                    except Exception as e:
                        print(f"  ⚠️ Error parsing product: {e}")
                        continue
                
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [ETSY] AgentQL error: {e}")
                return []
    
    def scrape_ebay(self, charm_name):
        """Scrape eBay using AgentQL's AI-powered queries"""
        print(f"🛒 [EBAY-AGENTQL] Scraping eBay for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(os.getcwd(), "playwright_data"),
                    channel="chrome" if os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") else None,
                    headless=False,
                    no_viewport=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                page = agentql.wrap(browser.new_page())
                
                url = f"https://www.ebay.com/sch/i.html?_nkw={charm_name.replace(' ', '+')}&_sop=12"
                print(f"🔗 [EBAY] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                time.sleep(3)
                
                page.screenshot(path="ebay_agentql_debug.png")
                print("📸 [EBAY] Screenshot saved")
                
                # Check for bot detection
                html = page.content()
                if 'interrupt' in html.lower() or 'captcha' in html.lower() or 'challenge' in html.lower():
                    print("❌ [EBAY] Bot detection triggered even with AgentQL")
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
                
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [EBAY] AgentQL error: {e}")
                return []
    
    def scrape_poshmark(self, charm_name):
        """Scrape Poshmark using AgentQL's AI-powered queries"""
        print(f"👗 [POSHMARK-AGENTQL] Scraping Poshmark for: {charm_name}")
        
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(os.getcwd(), "playwright_data"),
                    channel="chrome" if os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") else None,
                    headless=False,
                    no_viewport=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                page = agentql.wrap(browser.new_page())
                
                url = f"https://poshmark.com/search?query={charm_name.replace(' ', '+')}"
                print(f"🔗 [POSHMARK] Navigating to: {url}")
                page.goto(url, wait_until="load", timeout=60000)
                
                time.sleep(3)
                
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
                
                browser.close()
                return listings
                
            except Exception as e:
                print(f"❌ [POSHMARK] AgentQL error: {e}")
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
    
    scraper = AgentQLMarketplaceScraper()
    results = scraper.scrape_all("West Virginia charm")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {len(results)} total listings")
    print(f"{'='*60}\n")
    
    for listing in results:
        print(f"  {listing['platform']}: {listing['title'][:60]}... - ${listing['price']}")
    
    return results


if __name__ == "__main__":
    test_agentql_scraper()
