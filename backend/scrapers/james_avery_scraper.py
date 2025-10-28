"""
Enhanced James Avery Website Scraper for CharmTracker
Fetches official product details, images, and retired status
"""

import logging
from typing import Dict, Optional, List, Set
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import re
import asyncio
import json
import os
import time
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.scraper')

logger = logging.getLogger(__name__)

# Constants
DELAY = float(os.getenv('SCRAPER_DELAY', '2'))  # Delay between requests
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
# Only use proxy if properly configured
PROXY = os.getenv('AIOHTTP_PROXY') if os.getenv('AIOHTTP_PROXY', '').startswith(('http://', 'https://')) else None


class JamesAveryScraper:
    """James Avery official website scraper"""
    
    def __init__(self):
        self.base_url = "https://www.jamesavery.com"
        self.browse_url = f"{self.base_url}/charms"
        self.search_url = f"{self.base_url}/search"
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        self.session = None
        self.last_request_time = 0  # Track time of last request for rate limiting
        self.timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        
    async def __aenter__(self):
        """Set up async context manager"""
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=False, limit=5)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                trust_env=True
            )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context manager"""
        if self.session:
            await self.session.close()
            self.session = None
        
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """Make an HTTP request with retry logic and adaptive rate limiting"""
        MAX_RETRIES = 3
        MIN_DELAY = DELAY
        MAX_DELAY = DELAY * 10
        
        if not self.session:
            await self.__aenter__()
        
        # Ensure minimum delay between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < MIN_DELAY:
            await asyncio.sleep(MIN_DELAY - time_since_last)
            
        for attempt in range(MAX_RETRIES):
            try:
                self.last_request_time = time.time()
                delay = MIN_DELAY * (2 ** attempt)  # Exponential backoff
                delay = min(delay, MAX_DELAY)
                
                request_kwargs = {
                    'params': params,
                    'headers': self.headers,
                    'allow_redirects': True
                }
                if PROXY:
                    request_kwargs['proxy'] = PROXY
                    
                async with self.session.get(url, **request_kwargs) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Log successful request timing
                        duration = time.time() - self.last_request_time
                        logger.debug(f"Request to {url} completed in {duration:.2f}s")
                        return content
                        
                    elif response.status == 429:  # Too Many Requests
                        logger.warning(f"Rate limited on attempt {attempt + 1}")
                        # Get retry_after from headers or use exponential backoff
                        retry_after = int(response.headers.get('Retry-After', delay))
                        retry_delay = max(retry_after, delay)
                        logger.info(f"Waiting {retry_delay}s before retry")
                        await asyncio.sleep(retry_delay)
                        continue
                        
                    elif response.status >= 500:
                        logger.warning(f"Server error {response.status} on attempt {attempt + 1}")
                        await asyncio.sleep(delay)
                        continue
                        
                    else:
                        logger.warning(f"Request failed with status {response.status}")
                        if attempt == MAX_RETRIES - 1:
                            return None
                        await asyncio.sleep(delay)
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Network error on attempt {attempt + 1}: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(delay)
                
        return None
            
    async def _get_all_product_urls(self) -> Set[str]:
        """Get all product URLs from main James Avery charms page"""
        all_product_urls = set()
        
        # Use main charms page with pagination - NO CATEGORIES
        base_url = f"{self.base_url}/charms"
        page = 0
        consecutive_empty_pages = 0
        MAX_PAGES = 100  # Adjust if needed
        
        logger.info("Scraping ALL charms from main page (no categories)")
        
        while page < MAX_PAGES:
            # James Avery uses start parameter for pagination
            url = f"{base_url}?start={page * 30}&sz=30"
            logger.info(f"Fetching page {page + 1}: {url}")
            
            html = await self._make_request(url)
            
            if not html:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 2:
                    break
                page += 1
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            product_links = set()
            
            # Find all product links on this page
            # Try multiple selectors
            for link in soup.find_all('a', href=re.compile(r'/charms/[^/]+/[A-Z]+-\d+\.html')):
                product_url = urljoin(self.base_url, link['href'])
                product_links.add(product_url)
            
            # Also try product tiles/cards
            for tile in soup.find_all(['div', 'article'], class_=re.compile(r'product|tile|card', re.I)):
                link = tile.find('a', href=re.compile(r'/charms/'))
                if link and link.get('href'):
                    product_url = urljoin(self.base_url, link['href'])
                    if '/charms/' in product_url and '.html' in product_url:
                        product_links.add(product_url)
            
            if not product_links:
                consecutive_empty_pages += 1
                logger.info(f"No products found on page {page + 1}")
                if consecutive_empty_pages >= 3:
                    logger.info("No more products found, stopping")
                    break
            else:
                consecutive_empty_pages = 0
                all_product_urls.update(product_links)
                logger.info(f"Found {len(product_links)} products on page {page + 1} (Total: {len(all_product_urls)})")
            
            page += 1
            await asyncio.sleep(DELAY)
        
        logger.info(f"Total products discovered: {len(all_product_urls)}")
        return all_product_urls
    
    async def get_all_charms(self) -> List[Dict]:
        """
        Fetch all charms from James Avery website
        Returns complete list of charms with details
        """
        all_charms = []
        try:
            logger.info("Starting charm collection process...")
            
            # Get initial charm listing page
            html = await self._make_request(self.browse_url)
            if not html:
                logger.error("Failed to get main charms page")
                return []
            
            # Parse category URLs
            soup = BeautifulSoup(html, 'html.parser')
            category_links = set()
            
            # Direct category URLs - these are the main charm categories
            MAIN_CATEGORIES = [
                'heart-charms',
                'religious-charms',
                'animal-charms',
                'birthstone-charms',
                'charm-letters',
                'seasonal-charms',
                'travel-charms',
                'hobby-charms',
                'milestone-charms'
            ]
            
            # Add main categories first
            category_urls = [f"{self.base_url}/charms/{category}" for category in MAIN_CATEGORIES]
            
            # Backup method: Parse from navigation
            nav_urls = set()
            # Method 1: Navigation menu
            for nav in soup.find_all(['nav', 'ul', 'div'], {'class': re.compile(r'.*nav.*|.*menu.*')}):
                for link in nav.find_all('a', href=re.compile(r'/charms/[^/]+/?$')):
                    if link.get('href'):
                        nav_urls.add(urljoin(self.base_url, link['href']))
            
            # Method 2: Category grid/list
            for container in soup.find_all('div', {'class': re.compile(r'.*category.*|.*grid.*|.*list.*')}):
                for link in container.find_all('a', href=re.compile(r'/charms/[^/]+/?$')):
                    if link.get('href'):
                        nav_urls.add(urljoin(self.base_url, link['href']))
            
            # Combine both sets of URLs
            category_urls.extend(list(nav_urls))
            category_urls = list(set(category_urls))  # Remove duplicates
            
            # Filter out non-charm categories
            category_urls = [url for url in category_urls 
                           if '/charms/' in url and 'collection' not in url.lower()]
            
            logger.info(f"Found {len(category_urls)} category URLs")
            
            # Process each category
            all_product_urls = set()
            MAX_PAGES_PER_CATEGORY = 50  # Reasonable limit to avoid infinite loops
            
            for category_url in category_urls:
                page = 1
                consecutive_empty_pages = 0
                
                while page <= MAX_PAGES_PER_CATEGORY:
                    url = f"{category_url}?page={page}"
                    html = await self._make_request(url)
                    
                    if not html:
                        logger.warning(f"Failed to fetch page {page} of {category_url}")
                        break
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    product_links = set()
                    
                    # Find product containers
                    for container in soup.find_all('div', {'class': re.compile(r'.*product.*')}):
                        link = container.find('a', href=re.compile(r'/charms/.*\.html'))
                        if link and link.get('href'):
                            product_urls = urljoin(self.base_url, link['href'])
                            product_links.add(product_urls)
                    
                    # If no products found on consecutive pages, stop
                    if not product_links:
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= 2:
                            logger.info(f"No more products found in category {category_url} after {page} pages")
                            break
                    else:
                        consecutive_empty_pages = 0
                        all_product_urls.update(product_links)
                        logger.info(f"Found {len(product_links)} products on page {page} of category {category_url}")
                    
                    page += 1
                    await asyncio.sleep(DELAY)  # Respect rate limits
                
                if page > MAX_PAGES_PER_CATEGORY:
                    logger.warning(f"Reached maximum page limit for category {category_url}")
            
            logger.info(f"Found {len(all_product_urls)} total charm URLs")            # Fetch details for each charm in parallel batches
            all_charms = []
            batch_size = 5  # Process 5 charms at a time
            
            for i in range(0, len(all_product_urls), batch_size):
                batch_urls = list(all_product_urls)[i:i + batch_size]
                tasks = [self._get_product_page(url) for url in batch_urls]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out errors and add successful results
                valid_results = [
                    result for result in batch_results 
                    if isinstance(result, dict)
                ]
                all_charms.extend(valid_results)
                
                logger.info(f"Processed {len(all_charms)}/{len(all_product_urls)} charms")
                await asyncio.sleep(DELAY)  # Delay between batches
            
            return all_charms
            
        except Exception as e:
            logger.error(f"Error fetching all charms: {str(e)}")
            return []
            
    async def _get_category_urls(self) -> List[str]:
        """Get all charm category URLs"""
        try:
            html = await self._make_request(self.browse_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # Find category links - look for links in the navigation or category sections
                category_links = []
                
                # Method 1: Try navigation menu
                nav_menu = soup.find('nav', {'class': re.compile(r'.*navigation.*')})
                if nav_menu:
                    category_links.extend(nav_menu.find_all('a', href=re.compile(r'/charms/.*')))
                
                # Method 2: Try category grid/list
                category_grid = soup.find('div', {'class': re.compile(r'.*(categories|grid|list).*')})
                if category_grid:
                    category_links.extend(category_grid.find_all('a', href=re.compile(r'/charms/.*')))
                
                # Method 3: Try direct category links
                category_links.extend(soup.find_all('a', href=re.compile(r'/charms/[^/]+$')))
                
                category_urls = [
                    urljoin(self.base_url, link['href'])
                    for link in category_links
                    if '/charms/' in link['href'] and 'collection' not in link['href'].lower()
                ]
                
                return list(set(category_urls))
            return []
                    
        except Exception as e:
            logger.error(f"Error getting category URLs: {str(e)}")
            return []
            
    async def _get_product_urls_from_category(self, category_url: str) -> Set[str]:
        """Get all product URLs from a category page"""
        product_urls = set()
        page = 1
        
        while True:
            try:
                url = f"{category_url}?page={page}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status != 200:
                            break
                            
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find product links - try multiple selectors
                        links = []
                        
                        # Method 1: Product grid items
                        product_grid = soup.find('div', {'class': re.compile(r'.*(product-grid|products-grid).*')})
                        if product_grid:
                            links.extend(product_grid.find_all('a', href=re.compile(r'/charms/.*\.html')))
                        
                        # Method 2: Product list items
                        product_list = soup.find_all('div', {'class': re.compile(r'.*product-item.*')})
                        for item in product_list:
                            if item_link := item.find('a', href=re.compile(r'/charms/.*\.html')):
                                links.append(item_link)
                        
                        # Method 3: Direct product links
                        links.extend(soup.find_all('a', href=re.compile(r'/charms/[^/]+/[^/]+\.html')))
                        
                        page_urls = {
                            urljoin(self.base_url, link['href'])
                            for link in links
                            if 'charms' in link['href'] and '.html' in link['href']
                        }
                        
                        if not page_urls:
                            break
                            
                        product_urls.update(page_urls)
                        page += 1
                        
                        # Small delay between pages
                        await asyncio.sleep(0.5)
                        
            except Exception as e:
                logger.error(f"Error on category page {page}: {str(e)}")
                break
                
        return product_urls
        
    async def get_charm_details(
        self, 
        charm_name: str
    ) -> Optional[Dict]:
        """
        Get official charm details from James Avery website
        Returns charm info including images, description, material, and status
        """
        try:
            # First, search for the charm
            search_results = await self._search_charm(charm_name)
            if not search_results:
                logger.info(f"No results found for {charm_name} on James Avery")
                return None
            
            # Get the first matching result
            product_url = search_results[0].get('url')
            if not product_url:
                return None
            
            # Fetch detailed product page
            product_details = await self._get_product_page(product_url)
            
            return product_details
            
        except Exception as e:
            logger.error(f"Error getting James Avery details for {charm_name}: {str(e)}")
            return None
    
    async def _search_charm(self, charm_name: str) -> List[Dict]:
        """Search James Avery website"""
        try:
            params = {
                'q': charm_name,
                'lang': 'default',
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.search_url, 
                    params=params, 
                    headers=headers,
                    allow_redirects=True
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        results = self._parse_search_results(html)
                        logger.info(f"Found {len(results)} results for '{charm_name}'")
                        return results
                    else:
                        logger.warning(f"Search returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching James Avery: {str(e)}", exc_info=True)
            return []
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results page"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find product tiles - try multiple selectors
            products = soup.find_all('div', class_=re.compile(r'product-tile'))
            
            # If no product tiles, try alternative selectors
            if not products:
                products = soup.find_all('div', class_=re.compile(r'product-item|product-card|product'))
            
            # Also try looking for links with product URLs
            if not products:
                products = soup.find_all('a', href=re.compile(r'/products/'))
            
            logger.info(f"Found {len(products)} potential product elements")
            
            for idx, product in enumerate(products):
                try:
                    # Extract URL - try multiple methods
                    link = None
                    url = ''
                    
                    # Method 1: Find link with product-related class
                    link = product.find('a', class_=re.compile(r'product-tile__link|product-link|tile-link'))
                    
                    # Method 2: Find any link with /products/ in href
                    if not link:
                        link = product.find('a', href=re.compile(r'/products/|/product/'))
                    
                    # Method 3: If the product element itself is a link
                    if not link and product.name == 'a':
                        link = product
                    
                    # Method 4: Find ANY link inside the product element
                    if not link:
                        link = product.find('a')
                    
                    if link:
                        url = link.get('href', '')
                        if url and not url.startswith('http'):
                            url = f"{self.base_url}{url}"
                    
                    # Extract title - try multiple methods
                    title = ''
                    
                    # Method 1: Look for title in common heading tags
                    title_elem = product.find('h3', class_=re.compile(r'product-tile__name|product-name|product-title|name|title'))
                    if not title_elem:
                        title_elem = product.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    
                    # Method 2: Look for product name in spans or divs
                    if not title_elem:
                        title_elem = product.find(['span', 'div'], class_=re.compile(r'name|title|product-name'))
                    
                    # Method 3: Try aria-label or title attribute on link
                    if not title_elem and link:
                        title = link.get('aria-label', '') or link.get('title', '')
                        if not title:
                            title_elem = link
                    
                    # Method 4: Extract from image alt text as fallback
                    if not title and not title_elem:
                        img = product.find('img')
                        if img:
                            title = img.get('alt', '')
                    
                    if title_elem and not title:
                        title = title_elem.text.strip()
                    
                    # Extract image - try multiple attributes
                    img_elem = product.find('img')
                    image = ''
                    if img_elem:
                        # Try different image attributes
                        image = (img_elem.get('src') or 
                                img_elem.get('data-src') or 
                                img_elem.get('data-lazy-src') or 
                                img_elem.get('data-zoom-src') or '')
                        
                        # Clean and format URL - filter out generic images
                        if image:
                            image_lower = image.lower()
                            # Filter out navigation/generic images
                            exclude_patterns = ['placeholder', 'loading', 'flyout', 'navigation', 'nav-', 'menu', 'logo', 'banner']
                            if any(pattern in image_lower for pattern in exclude_patterns):
                                image = ''
                            elif not image.startswith('http'):
                                image = f"{self.base_url}{image}"
                    
                    if url and title:
                        results.append({
                            'url': url,
                            'title': title,
                            'image': image
                        })
                        logger.debug(f"Result {idx+1}: {title} - Image: {bool(image)}")
                    else:
                        logger.debug(f"Skipped element {idx+1}: url={bool(url)}, title={bool(title)}")
                        
                except Exception as e:
                    logger.debug(f"Error parsing search result {idx}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}", exc_info=True)
            
        return results
    
    async def _get_product_page(self, url: str) -> Optional[Dict]:
        """Fetch and parse product detail page"""
        try:
            html = await self._make_request(url)
            if html:
                return self._parse_product_page(html, url)
            return None
                    
        except Exception as e:
            logger.error(f"Error fetching product page: {str(e)}", exc_info=True)
            return None
    
    def _parse_product_page(self, html: str, url: str) -> Optional[Dict]:
        """Parse product detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to extract JSON-LD first
            json_ld = None
            for script in soup.find_all('script', {'type': 'application/ld+json'}):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        json_ld = data
                        break
                except:
                    continue
            
            # Extract product name
            name_elem = soup.find('h1', class_=re.compile(r'product-name'))
            if not name_elem:
                name_elem = soup.find('h1')
            name = name_elem.text.strip() if name_elem else ''
            
            # Extract description
            desc_elem = soup.find('div', class_=re.compile(r'product-description'))
            if not desc_elem:
                desc_elem = soup.find('div', {'itemprop': 'description'})
            description = desc_elem.text.strip() if desc_elem else ''
            
            # Extract SKU and material
            sku = None
            material = None
            
            # Try to get SKU from URL first (most reliable)
            sku_match = re.search(r'/(?:CM|MS|KIT)-\d+', url)
            if sku_match:
                sku = sku_match.group(0).lstrip('/')
            
            # Try from structured data
            if not sku and json_ld:
                if isinstance(json_ld, dict):
                    # Try standard schema.org properties
                    sku = (json_ld.get('sku') or 
                          json_ld.get('productID') or 
                          json_ld.get('mpn') or  # Manufacturer Part Number
                          json_ld.get('identifier'))
                    
                    # Check offers array for SKUs
                    if not sku and 'offers' in json_ld:
                        offers = json_ld['offers']
                        if isinstance(offers, list):
                            for offer in offers:
                                if isinstance(offer, dict):
                                    sku = (offer.get('sku') or 
                                          offer.get('productID') or 
                                          offer.get('mpn'))
                                    if sku:
                                        break
                        elif isinstance(offers, dict):
                            sku = (offers.get('sku') or 
                                  offers.get('productID') or 
                                  offers.get('mpn'))
            
            # Try HTML elements
            if not sku:
                # Method 1: Data attributes
                product_div = soup.find(['div', 'form'], {'data-product-id': True})
                if product_div:
                    sku = product_div.get('data-product-id')
                
                # Method 2: SKU/Product code element
                if not sku:
                    sku_patterns = [
                        r'(?:CM|MS|KIT)-\d+',
                        r'Product\s+(?:Code|ID):\s*([A-Z0-9-]+)',
                        r'SKU:\s*([A-Z0-9-]+)',
                        r'Item\s+#:\s*([A-Z0-9-]+)'
                    ]
                    
                    # Look in text content
                    for pattern in sku_patterns:
                        for elem in soup.find_all(['span', 'div', 'p']):
                            if elem.text:
                                match = re.search(pattern, elem.text, re.I)
                                if match:
                                    sku = match.group(1) if len(match.groups()) > 0 else match.group(0)
                                    break
                        if sku:
                            break
            
            # Clean up SKU if found
            if sku:
                # Remove any surrounding whitespace or special characters
                sku = re.sub(r'^[^A-Z0-9]+|[^A-Z0-9-]+$', '', sku.upper())
                # Validate format
                if not re.match(r'^(?:CM|MS|KIT)-\d+$', sku):
                    sku = None
            
            # Determine material
            material_map = {
                'sterling silver': 'Silver',
                '14k gold': 'Gold',
                'white gold': 'White Gold',
                'rose gold': 'Rose Gold'
            }
            
            # Try to get material from structured data
            if json_ld:
                material_prop = json_ld.get('material', '').lower()
                for key, value in material_map.items():
                    if key in material_prop:
                        material = value
                        break
            
            # Try to get from page content if not found
            if not material:
                material_elem = soup.find(['span', 'div'], class_=re.compile(r'material|metal', re.I))
                if material_elem:
                    material_text = material_elem.text.strip().lower()
                    for key, value in material_map.items():
                        if key in material_text:
                            material = value
                            break
            
            # Default to Silver if still not found
            if not material:
                material = 'Silver'  # Default
            
            # Check if retired
            is_retired = False
            status = 'Active'
            
            # Look for "retired" or "discontinued" text
            if 'retired' in html.lower() or 'discontinued' in html.lower():
                is_retired = True
                status = 'Retired'
            
            # Check for "out of stock" or "unavailable"
            availability_elem = soup.find('button', class_=re.compile(r'add-to-cart'))
            if availability_elem:
                button_text = availability_elem.text.lower()
                if 'unavailable' in button_text or 'out of stock' in button_text:
                    # Could be temporarily out of stock or retired
                    # Check elsewhere for confirmation
                    pass
            else:
                # No add to cart button might mean retired
                is_retired = True
                status = 'Retired'
            
            # Extract price - try multiple methods
            price = None
            # Method 1: Structured data
            if json_ld and 'offers' in json_ld:
                try:
                    price_str = json_ld['offers'].get('price')
                    if price_str:
                        price = float(str(price_str).replace(',', ''))
                except (ValueError, TypeError):
                    pass
            
            # Method 2: Price element
            if not price:
                for price_class in ['price-sales', 'product-price', 'price']:
                    price_elem = soup.find(['span', 'div'], class_=re.compile(price_class, re.I))
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                                break
                            except ValueError:
                                continue
            
            # Method 3: Meta tags
            if not price:
                meta_price = soup.find('meta', {'property': 'product:price:amount'})
                if meta_price:
                    try:
                        price = float(meta_price.get('content', '0').replace(',', ''))
                    except ValueError:
                        pass
            
            # Extract images
            images = []
            
            # Helper function to check if image URL is valid product image
            def is_valid_product_image(img_url):
                if not img_url:
                    return False
                # Skip data URIs and invalid URLs
                if img_url.startswith('data:') or len(img_url) < 10:
                    return False
                img_url_lower = img_url.lower()
                # Filter out generic/navigation/promotional images
                exclude_patterns = [
                    'placeholder', 'logo', 'banner', 'navigation', 
                    'flyout', 'global-navigation', 'nav-', 'menu',
                    'icon', 'sprite', 'back_to_top', 'cross.svg',
                    'search.svg', 'wishlist.svg', 'location', 'account',
                    'magnifying', 'gift-central', 'category-thumbnail',
                    'swatch-', '/swatch'  # Exclude color swatches
                ]
                # Check if it's a Scene7 product image (best quality)
                is_scene7 = 'scene7.com/is/image/JamesAvery/' in img_url
                
                # Check for product-specific patterns
                has_product_code = bool(re.search(r'(CM-|MS_CM-|MS_KIT-)\d+', img_url))
                
                exclude_match = any(pattern in img_url_lower for pattern in exclude_patterns)
                
                # Prefer Scene7 images with product codes
                return (is_scene7 and has_product_code) or (is_scene7 and not exclude_match)
            
            # Method 1: Look for JSON-LD structured data (most reliable)
            try:
                json_ld = soup.find('script', {'type': 'application/ld+json'})
                if json_ld:
                    import json
                    data = json.loads(json_ld.string)
                    if isinstance(data, dict):
                        img_url = data.get('image', '')
                        if isinstance(img_url, list):
                            for url in img_url:
                                if is_valid_product_image(url):
                                    if not url.startswith('http'):
                                        url = f"{self.base_url}{url}"
                                    if url not in images:
                                        images.append(url)
                        elif img_url and is_valid_product_image(img_url):
                            if not img_url.startswith('http'):
                                img_url = f"{self.base_url}{img_url}"
                            images.append(img_url)
            except Exception as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
            
            # Method 2: Extract all Scene7 URLs from HTML using regex
            if not images:
                # Find all Scene7 image URLs in the HTML
                scene7_pattern = r'https://jamesavery\.scene7\.com/is/image/JamesAvery/([^?&"\'\s]+)'
                scene7_matches = re.findall(scene7_pattern, html)
                
                for img_id in scene7_matches:
                    full_url = f"https://jamesavery.scene7.com/is/image/JamesAvery/{img_id}"
                    if is_valid_product_image(full_url) and full_url not in images:
                        images.append(full_url)
                        if len(images) >= 5:  # Max 5 images
                            break
            
            # Method 3: Look for meta property="og:image"
            if not images:
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    img_url = og_image.get('content', '')
                    if is_valid_product_image(img_url):
                        if not img_url.startswith('http'):
                            img_url = f"{self.base_url}{img_url}"
                        images.append(img_url)
            
            # Method 4: Look for itemprop="image" 
            if not images:
                schema_imgs = soup.find_all(['img', 'meta'], {'itemprop': 'image'})
                for elem in schema_imgs:
                    img_url = elem.get('content', elem.get('src', elem.get('data-src', '')))
                    if is_valid_product_image(img_url):
                        if not img_url.startswith('http'):
                            img_url = f"{self.base_url}{img_url}"
                        if img_url not in images:
                            images.append(img_url)
                            if len(images) >= 3:
                                break
            
            # Extract additional metadata
            sku = None
            sku_elem = soup.find('span', class_=re.compile(r'product-sku|sku|product-number|item-number'))
            if sku_elem:
                sku = re.search(r'[A-Z0-9-]+', sku_elem.text.strip())
                if sku:
                    sku = sku.group(0)
            
            # Extract category breadcrumbs
            breadcrumbs = []
            breadcrumb_nav = soup.find('nav', {'aria-label': re.compile(r'.*breadcrumb.*', re.I)})
            if breadcrumb_nav:
                for crumb in breadcrumb_nav.find_all('a'):
                    breadcrumbs.append(crumb.text.strip())
            
            # Extract metal options - try multiple methods
            metal_options = []
            
            # Method 1: Variant selector
            variant_script = soup.find('script', string=re.compile(r'var\s+variants\s*='))
            if variant_script:
                try:
                    variants_match = re.search(r'var\s+variants\s*=\s*(\[.*?\]);', variant_script.string, re.DOTALL)
                    if variants_match:
                        import json
                        variants = json.loads(variants_match.group(1))
                        for variant in variants:
                            if 'metal' in variant:
                                metal_options.append({
                                    'type': variant['metal'],
                                    'value': variant.get('id', ''),
                                    'available': variant.get('available', False),
                                    'price': variant.get('price', None)
                                })
                except:
                    pass
            
            # Method 2: Metal selector
            if not metal_options:
                metal_select = soup.find('select', {'name': re.compile(r'.*metal.*', re.I)})
                if metal_select:
                    for option in metal_select.find_all('option'):
                        metal_text = option.text.strip()
                        metal_value = option.get('value', '')
                        if metal_text and metal_value and metal_text.lower() not in ['select', 'choose']:
                            # Try to get price from data attribute or text
                            price_match = re.search(r'\(([\d,.]+)\)', metal_text)
                            try:
                                price = float(price_match.group(1).replace(',', '')) if price_match else None
                            except ValueError:
                                price = None
                            
                            metal_options.append({
                                'type': re.sub(r'\s*\(.*?\)', '', metal_text),
                                'value': metal_value,
                                'available': not bool(option.get('disabled')),
                                'price': price
                            })
            
            # Method 3: Material tags or text
            if not metal_options:
                metal_texts = []
                for elem in soup.find_all(['span', 'div', 'p'], string=re.compile(r'(?:sterling|silver|gold|metal)', re.I)):
                    text = elem.text.strip().lower()
                    if 'sterling silver' in text:
                        metal_texts.append('Sterling Silver')
                    elif '14k gold' in text:
                        metal_texts.append('14K Gold')
                    elif 'white gold' in text:
                        metal_texts.append('White Gold')
                    elif 'rose gold' in text:
                        metal_texts.append('Rose Gold')
                
                for metal in set(metal_texts):
                    metal_options.append({
                        'type': metal,
                        'value': metal.lower().replace(' ', '-'),
                        'available': True,
                        'price': None
                    })
            
            # Extract any size options
            sizes = []
            size_select = soup.find('select', {'name': re.compile(r'.*size.*', re.I)})
            if size_select:
                for option in size_select.find_all('option'):
                    size_text = option.text.strip()
                    if size_text and size_text.lower() not in ['select size', 'choose size']:
                        sizes.append(size_text)

            # Detect if the item is exclusive or part of a collection
            is_exclusive = 'exclusive' in html.lower()
            collection = None
            collection_links = soup.find_all('a', href=re.compile(r'/collections/[^/]+/?$'))
            if collection_links:
                collection = collection_links[0].text.strip()
            
            # Return structured data
            product_data = {
                'name': name,
                'description': description or f"Individual {name} charm from James Avery.",
                'sku': sku,
                'material': material,
                'metal_options': metal_options,
                'sizes': sizes if sizes else None,
                'status': status,
                'is_retired': is_retired,
                'official_price': price,
                'images': images,
                'official_url': url,
                'category_path': breadcrumbs,
                'is_exclusive': is_exclusive,
                'collection': collection,
                'scraped_at': datetime.utcnow().isoformat(),
                'in_stock': not is_retired and bool(price)
            }
            
            logger.info(f"Parsed product: {name} - Found {len(images)} images")
            if metal_options:
                logger.debug(f"Metal options: {metal_options}")
            
            return product_data if name else None
            
        except Exception as e:
            logger.error(f"Error parsing product page: {str(e)}")
            return None
    
    async def check_if_retired(self, charm_name: str) -> bool:
        """Quick check if a charm is retired"""
        try:
            details = await self.get_charm_details(charm_name)
            if details:
                return details.get('is_retired', False)
            return False
        except Exception as e:
            logger.error(f"Error checking retired status: {str(e)}")
            return False


async def test_scraper():
    """Test function to validate scraper functionality"""
    async with JamesAveryScraper() as scraper:
        # Test specific charm URLs
        test_urls = [
            "https://www.jamesavery.com/charms/heart-to-heart-charm/CM-1979.html",
            "https://www.jamesavery.com/charms/flared-cross-charm/CM-2230.html",
            "https://www.jamesavery.com/charms/enamel-halloween-dinosaur-costume-charm/CM-6139.html"
        ]
        
        logger.info("Starting scraper test...")
        for url in test_urls:
            try:
                details = await scraper._get_product_page(url)
                if details:
                    logger.info(f"\nTested URL: {url}")
                    logger.info(f"Name: {details.get('name', 'N/A')}")
                    logger.info(f"Price: ${details.get('official_price', 'N/A')}")
                    logger.info(f"Status: {details.get('status', 'N/A')}")
                    logger.info(f"Metal Options: {', '.join(m.get('type', '') for m in details.get('metal_options', []))}")
                    logger.info(f"Images Found: {len(details.get('images', []))}")
                    logger.info(f"SKU: {details.get('sku', 'N/A')}")
                    logger.info("-" * 50)
                else:
                    logger.error(f"Failed to get details for {url}")
            except Exception as e:
                logger.error(f"Error testing {url}: {str(e)}")
        
        # Test search functionality
        test_searches = ["heart charm", "cross charm", "baby feet"]
        for search_term in test_searches:
            try:
                results = await scraper._search_charm(search_term)
                logger.info(f"\nSearch results for '{search_term}':")
                logger.info(f"Found {len(results)} results")
                if results:
                    sample = results[0]
                    logger.info(f"First result: {sample.get('title', 'N/A')}")
                    logger.info(f"URL: {sample.get('url', 'N/A')}")
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Error testing search for {search_term}: {str(e)}")


# Initialize scraper instance
james_avery_scraper = JamesAveryScraper()

# Run test if executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scraper())