"""
Enhanced James Avery scraper methods
"""

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
            html = await self._make_request(url)
            
            if not html:
                break
                
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
            await asyncio.sleep(DELAY)
            
        except Exception as e:
            logger.error(f"Error on category page {page}: {str(e)}")
            break
            
    return product_urls

async def _get_product_page(self, url: str) -> Optional[Dict]:
    """Fetch and parse product details page"""
    try:
        html = await self._make_request(url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract structured data
        json_ld = None
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if '@type' in data and data['@type'] == 'Product':
                    json_ld = data
                    break
            except:
                continue
        
        if not json_ld:
            return None
        
        # Get main product image
        image_url = None
        if 'image' in json_ld:
            if isinstance(json_ld['image'], list):
                image_url = json_ld['image'][0]
            else:
                image_url = json_ld['image']
                
        # Get all additional images
        image_gallery = []
        gallery_container = soup.find('div', {'class': re.compile(r'.*product-gallery.*')})
        if gallery_container:
            for img in gallery_container.find_all('img', {'src': True}):
                img_url = urljoin(self.base_url, img['src'])
                if img_url and img_url not in image_gallery:
                    image_gallery.append(img_url)
        
        # Check availability and retired status
        availability = json_ld.get('offers', {}).get('availability', '')
        is_retired = 'Retired' in soup.text or 'No Longer Available' in soup.text
        status = 'Retired' if is_retired else 'Active'
        
        # Get price
        price = None
        price_elem = soup.find('span', {'class': re.compile(r'.*price.*')})
        if price_elem:
            price_text = price_elem.text.strip()
            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
        
        # Get metal options
        metals = set()
        metal_selectors = soup.find_all('select', {'name': re.compile(r'.*metal.*', re.I)})
        for select in metal_selectors:
            for option in select.find_all('option'):
                metal = option.text.strip()
                if metal and metal.lower() not in ['select', 'choose']:
                    metals.add(metal)
        
        return {
            'name': json_ld.get('name', '').replace(' Charm', ''),
            'description': json_ld.get('description', ''),
            'url': url,
            'price': price,
            'image_url': image_url,
            'additional_images': image_gallery,
            'status': status,
            'is_retired': is_retired,
            'metals': list(metals),
            'available': 'OutOfStock' not in availability
        }
                
    except Exception as e:
        logger.error(f"Error fetching product page {url}: {str(e)}")
        return None