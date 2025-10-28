"""
Debug script to check James Avery product page structure
"""
import asyncio
import os
import re
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from scrapers.james_avery_scraper import JamesAveryScraper

async def debug_images():
    # Load environment variables
    load_dotenv()
    
    scraper = JamesAveryScraper()
    
    try:
        async with scraper:
            # First try searching for a specific charm
            search_params = {"q": "Star Charm"}
            print("\nSearching for Star Charm...")
            search_html = await scraper._make_request(scraper.search_url, search_params)
            
            if search_html:
                soup = BeautifulSoup(search_html, 'html.parser')
                
                # Look for product JSON data
                print("\nLooking for product JSON data...")
                scripts = soup.find_all('script', {'type': 'application/ld+json'})
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if '@type' in data and data['@type'] == 'Product':
                            print("Found product data:")
                            if 'image' in data:
                                print(f"Images in JSON: {data['image']}")
                    except:
                        continue
                
                # Try different product link patterns
                print("\nLooking for product links...")
                patterns = [
                    ('Basic charm pattern', r'/products/[^/]+charm\b'),
                    ('Category pattern', r'/charms/[^/]+'),
                    ('Product pattern', r'/products/[^/]+')
                ]
                
                for pattern_name, pattern in patterns:
                    links = soup.find_all('a', href=re.compile(pattern, re.I))
                    print(f"\n{pattern_name}:")
                    for link in links:
                        print(f"Found link: {link['href']}")
                        
                        # Try to get product page
                        product_url = urljoin(scraper.base_url, link['href'])
                        print(f"\nFetching product page: {product_url}")
                        
                        product_html = await scraper._make_request(product_url)
                        if product_html:
                            product_soup = BeautifulSoup(product_html, 'html.parser')
                            
                            # Try different image selectors
                            print("\nTrying various image selectors:")
                            selectors = [
                                ('Product image', 'img.product-image'),
                                ('Gallery image', 'img.product-gallery__image'),
                                ('Main product', 'img[itemprop="image"]'),
                                ('Zoom image', 'img[data-zoom]'),
                                ('All product images', 'img[src*="products"]')
                            ]
                            
                            for selector_name, selector in selectors:
                                images = product_soup.select(selector)
                                if images:
                                    print(f"\n{selector_name}:")
                                    for img in images:
                                        print(f"src: {img.get('src', 'No src')}")
                                        print(f"data-src: {img.get('data-src', 'No data-src')}")
                                        print(f"data-zoom: {img.get('data-zoom', 'No zoom')}")
                                        print("-" * 50)
                            
                            # Look for structured data
                            print("\nChecking structured data:")
                            structured_data = product_soup.find_all('script', {'type': 'application/ld+json'})
                            for data in structured_data:
                                try:
                                    json_data = json.loads(data.string)
                                    if '@type' in json_data and json_data['@type'] == 'Product':
                                        print("Found product structured data:")
                                        print(json.dumps(json_data, indent=2))
                                except:
                                    continue
                
                print("\nDebug complete!")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_images())