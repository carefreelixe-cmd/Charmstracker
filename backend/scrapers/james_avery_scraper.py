"""
James Avery Website Scraper for CharmTracker
Fetches official product details, images, and retired status
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class JamesAveryScraper:
    """James Avery official website scraper"""
    
    def __init__(self):
        self.base_url = "https://www.jamesavery.com"
        self.search_url = f"{self.base_url}/search"
        
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
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_product_page(html, url)
                    else:
                        logger.warning(f"Product page returned status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching product page: {str(e)}", exc_info=True)
            return None
    
    def _parse_product_page(self, html: str, url: str) -> Optional[Dict]:
        """Parse product detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
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
            
            # Extract material
            material = 'Silver'  # Default
            material_elem = soup.find('span', class_=re.compile(r'material'))
            if material_elem:
                material_text = material_elem.text.lower()
                if 'gold' in material_text:
                    material = 'Gold'
            elif 'gold' in name.lower() or 'gold' in description.lower():
                material = 'Gold'
            
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
            
            # Extract price
            price = None
            price_elem = soup.find('span', class_=re.compile(r'price-sales'))
            if not price_elem:
                price_elem = soup.find('span', {'itemprop': 'price'})
            
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'\$([\d,]+\.?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
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
                    'magnifying', 'gift-central', 'category-thumbnail'
                ]
                # Also check if it's a product images directory
                has_product_path = any(path in img_url_lower for path in ['/pdp/', '/products/', '-catalog/', 'items/', 'charms/'])
                exclude_match = any(pattern in img_url_lower for pattern in exclude_patterns)
                
                return has_product_path or not exclude_match
            
            # Method 1: Look for JSON-LD structured data (most reliable)
            try:
                json_ld = soup.find('script', {'type': 'application/ld+json'})
                if json_ld:
                    import json
                    data = json.loads(json_ld.string)
                    if isinstance(data, dict):
                        img_url = data.get('image', '')
                        if isinstance(img_url, list) and len(img_url) > 0:
                            img_url = img_url[0]
                        if is_valid_product_image(img_url):
                            if not img_url.startswith('http'):
                                img_url = f"{self.base_url}{img_url}"
                            images.append(img_url)
            except:
                pass
            
            # Method 2: Look for meta property="og:image"
            if not images:
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    img_url = og_image.get('content', '')
                    if is_valid_product_image(img_url):
                        if not img_url.startswith('http'):
                            img_url = f"{self.base_url}{img_url}"
                        images.append(img_url)
            
            # Method 3: Find images in product carousel with data attributes
            if not images:
                carousel = soup.find('div', class_=re.compile(r'product-carousel'))
                if carousel:
                    # Look for images with data-zoom-url or similar
                    imgs = carousel.find_all('img')
                    for img in imgs:
                        # Check multiple data attributes (James Avery uses lazy loading)
                        img_url = (img.get('data-zoom-url') or 
                                  img.get('data-src') or 
                                  img.get('data-lazy-src') or
                                  img.get('data-zoom-src') or
                                  img.get('src') or '')
                        
                        if is_valid_product_image(img_url):
                            if not img_url.startswith('http'):
                                img_url = f"{self.base_url}{img_url}"
                            if img_url not in images:
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
            
            # Return structured data
            product_data = {
                'name': name,
                'description': description or f"Individual {name} charm from James Avery.",
                'material': material,
                'status': status,
                'is_retired': is_retired,
                'official_price': price,
                'images': images,
                'official_url': url,
                'scraped_at': datetime.utcnow()
            }
            
            logger.info(f"Parsed product: {name} - Found {len(images)} images")
            if images:
                logger.debug(f"Image URLs: {images}")
            
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


# Initialize scraper instance
james_avery_scraper = JamesAveryScraper()