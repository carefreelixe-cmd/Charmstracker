"""
ScraperAPI Client - Uses ScraperAPI to bypass bot detection and fetch HTML
API handles proxies, CAPTCHAs, and JavaScript rendering automatically
"""
import requests
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import time

logger = logging.getLogger(__name__)


class ScraperAPIClient:
    """Client for fetching web pages through ScraperAPI"""
    
    def __init__(self, api_key='be8b8d16e40d4f8d81658ba7b2cc4b34'):
        self.api_key = api_key
        self.base_url = 'https://api.scraperapi.com/'
        logger.info(f"🔧 ScraperAPI initialized with key: {api_key[:20]}...")
    
    def fetch_page(self, url: str, render_js=True) -> Optional[str]:
        """
        Fetch HTML content from a URL using ScraperAPI
        
        Args:
            url: The target URL to scrape
            render_js: Whether to render JavaScript (default: True)
            
        Returns:
            HTML content as string, or None if failed
        """
        try:
            payload = {
                'api_key': self.api_key,
                'url': url,
                'render': 'true' if render_js else 'false'
            }
            
            logger.info(f"📡 Fetching: {url}")
            response = requests.get(self.base_url, params=payload, timeout=60)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully fetched {len(response.text)} bytes")
                return response.text
            else:
                logger.error(f"❌ ScraperAPI returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching page: {e}")
            return None
    
    def scrape_etsy(self, charm_name: str) -> List[Dict]:
        """Scrape Etsy marketplace using AgentQL (better for dynamic content and currency detection)"""
        try:
            logger.info(f"🎨 [ETSY-AGENTQL] Scraping: {charm_name}")
            
            # Import AgentQL scraper
            try:
                from scrapers.agentql_scraper import AgentQLMarketplaceScraper
            except ImportError as ie:
                logger.error(f"⚠️ AgentQL import failed: {ie}")
                return []
            
            # Use AgentQL for Etsy (handles dynamic content and currency detection)
            try:
                agentql_scraper = AgentQLMarketplaceScraper(headless=True)
                etsy_results = agentql_scraper.scrape_etsy(charm_name)
                logger.info(f"✅ [ETSY-AGENTQL] Got {len(etsy_results)} raw results")
            except Exception as scrape_err:
                logger.error(f"❌ [ETSY-AGENTQL] Scraping failed: {scrape_err}")
                import traceback
                traceback.print_exc()
                return []
            
            # Convert to our standardized format
            listings = []
            for item in etsy_results:
                try:
                    price = float(item.get('price', 0))
                    currency = item.get('currency', 'USD')
                    
                    # Validate price exists
                    if price <= 0:
                        logger.debug(f"⚠️ Skipping Etsy listing with invalid price: {price}")
                        continue
                    
                    listings.append({
                        'platform': 'etsy',
                        'marketplace': 'Etsy',
                        'title': item.get('title', '')[:200],
                        'price': price,
                        'currency': currency,
                        'url': item.get('url', ''),
                        'condition': item.get('condition', 'New'),
                        'seller': 'Etsy Seller',
                        'image_url': item.get('image_url', '')
                    })
                except Exception as e:
                    logger.debug(f"⚠️ Parse error: {e}")
                    continue
            
            logger.info(f"✅ [ETSY] Parsed {len(listings)} listings via AgentQL")
            return listings
            
        except Exception as e:
            logger.error(f"❌ [ETSY] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_ebay(self, charm_name: str) -> List[Dict]:
        """Scrape eBay using ScraperAPI's structured endpoint"""
        try:
            # Format search query for eBay (replace spaces with hyphens)
            search_query = charm_name.lower().replace(' ', '-')
            
            logger.info(f"🛒 [EBAY] Scraping: {charm_name}")
            
            # Use ScraperAPI's structured eBay endpoint
            payload = {
                'api_key': self.api_key,
                'query': search_query
            }
            
            response = requests.get(
                'https://api.scraperapi.com/structured/ebay/search/v2',
                params=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"❌ [EBAY] API returned status {response.status_code}")
                return []
            
            # Parse JSON response
            json_data = response.json()
            data = json_data.get('results', []) if isinstance(json_data, dict) else json_data
            logger.info(f"🛒 [EBAY] Found {len(data)} items")
            
            listings = []
            for item in data[:20]:
                try:
                    title = item.get('product_title', '').replace('Opens in a new window or tab', '').strip()
                    if not title:
                        continue
                    
                    # Handle price - can be single value or range
                    item_price = item.get('item_price', {})
                    price = None
                    
                    if isinstance(item_price, dict):
                        if 'value' in item_price:
                            price = float(item_price['value'])
                        elif 'from' in item_price and isinstance(item_price['from'], dict):
                            price = float(item_price['from'].get('value', 0))
                    
                    if not price or price <= 0:
                        continue
                    
                    # Validate price is reasonable (between $1 and $2000 for charms)
                    if price > 2000:
                        logger.debug(f"⚠️ Skipping eBay listing with high price: ${price}")
                        continue
                    
                    # Get other fields
                    image_url = item.get('image', '')
                    condition = item.get('condition', 'Used')
                    # ScraperAPI eBay structured data uses 'product_url' field
                    url_val = item.get('product_url', '') or item.get('url', '')
                    
                    # Extract seller info if available
                    seller_info = 'eBay Seller'
                    if item.get('seller_has_top_rated_plus'):
                        seller_info = 'Top Rated Plus Seller'
                    
                    listings.append({
                        'platform': 'ebay',
                        'marketplace': 'eBay',
                        'title': title[:200],
                        'price': price,
                        'url': url_val,
                        'condition': condition,
                        'seller': seller_info,
                        'image_url': image_url
                    })
                    
                except Exception as e:
                    logger.debug(f"⚠️ Parse error: {e}")
                    continue
            
            logger.info(f"✅ [EBAY] Parsed {len(listings)} listings")
            return listings
            
        except Exception as e:
            logger.error(f"❌ [EBAY] Error: {e}")
            return []
    
    def scrape_poshmark(self, charm_name: str) -> List[Dict]:
        """Scrape Poshmark using AgentQL (AI-powered scraping)"""
        try:
            logger.info(f"👗 [POSHMARK-AGENTQL] Scraping: {charm_name}")
            
            # Import AgentQL scraper
            try:
                from scrapers.agentql_scraper import AgentQLMarketplaceScraper
            except ImportError:
                logger.warning("⚠️ AgentQL not available, skipping Poshmark")
                return []
            
            # Use AgentQL for Poshmark (handles bot detection better)
            agentql_scraper = AgentQLMarketplaceScraper(headless=True)
            poshmark_results = agentql_scraper.scrape_poshmark(charm_name)
            
            # Convert to our standardized format
            listings = []
            for item in poshmark_results:
                try:
                    price = float(item.get('price', 0))
                    
                    # Validate price is reasonable (between $5 and $2000 for charms)
                    if price < 5 or price > 2000:
                        logger.debug(f"⚠️ Skipping Poshmark listing with unreasonable price: ${price}")
                        continue
                    
                    listings.append({
                        'platform': 'poshmark',
                        'marketplace': 'Poshmark',
                        'title': item.get('title', '')[:200],
                        'price': price,
                        'url': item.get('url', ''),
                        'condition': item.get('condition', 'Pre-owned'),
                        'seller': 'Poshmark Seller',
                        'image_url': item.get('image_url', '')
                    })
                except Exception as e:
                    logger.debug(f"⚠️ Parse error: {e}")
                    continue
            
            logger.info(f"✅ [POSHMARK] Parsed {len(listings)} listings via AgentQL")
            return listings
            
        except Exception as e:
            logger.error(f"❌ [POSHMARK] Error: {e}")
            return []
    
    def scrape_all(self, charm_name: str) -> List[Dict]:
        """Scrape all marketplaces for a charm in parallel for faster results"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 Scraping all marketplaces for: {charm_name}")
        logger.info(f"{'='*60}")
        
        all_listings = []
        
        # Use ThreadPoolExecutor to scrape all platforms in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all scraping tasks
            future_to_platform = {
                executor.submit(self.scrape_etsy, charm_name): 'etsy',
                executor.submit(self.scrape_ebay, charm_name): 'ebay',
                executor.submit(self.scrape_poshmark, charm_name): 'poshmark'
            }
            
            # Collect results as they complete
            results_map = {'etsy': [], 'ebay': [], 'poshmark': []}
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    listings = future.result()
                    results_map[platform] = listings
                    all_listings.extend(listings)
                    logger.info(f"✅ {platform.upper()}: {len(listings)} listings completed")
                except Exception as e:
                    logger.error(f"❌ Error scraping {platform}: {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 TOTAL: {len(all_listings)} listings found")
        logger.info(f"   🎨 Etsy: {len(results_map['etsy'])}")
        logger.info(f"   🛒 eBay: {len(results_map['ebay'])}")
        logger.info(f"   👗 Poshmark: {len(results_map['poshmark'])}")
        logger.info(f"{'='*60}\n")
        
        return all_listings


# Test function
if __name__ == "__main__":
    import json
    
    print("🧪 Testing ScraperAPI Client\n")
    
    scraper = ScraperAPIClient()
    results = scraper.scrape_all("James Avery Jesus Loves Me Charm")
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: {len(results)} total listings")
    print(f"{'='*60}\n")
    
    for listing in results[:10]:
        print(f"{listing['marketplace']}: {listing['title'][:60]}...")
        print(f"  💰 ${listing['price']}")
        print(f"  🔗 {listing['url'][:80]}\n")
    
    # Save results
    with open('test_scraperapi_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: test_scraperapi_results.json")
