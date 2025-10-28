"""
Debug version of James Avery charm update script
"""
import asyncio
import os
import re
import json
import sys
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from scrapers.james_avery_scraper import JamesAveryScraper

async def debug_charm(name: str):
    """Debug a single charm's search and scraping"""
    scraper = JamesAveryScraper()
    
    print(f"\n🔍 Debugging charm: {name}")
    
    async with scraper:
        # First try the search API
        print("\n1. Testing search API:")
        base_name = name.lower().replace('charm', '').strip()
        search_terms = [
            name,
            base_name,
            f"{base_name} charm",
            name.replace(' ', '+'),
            base_name.replace(' ', '+')
        ]
        
        for term in search_terms:
            print(f"\n   Searching for: {term}")
            search_url = f"https://www.jamesavery.com/products.json?q={quote(term)}"
            search_response = await scraper._make_request(search_url)
            
            if search_response:
                try:
                    data = json.loads(search_response)
                    if data.get('products'):
                        print(f"   Found {len(data['products'])} products")
                        for idx, product in enumerate(data['products'], 1):
                            print(f"\n   Product {idx}:")
                            print(f"   - Title: {product.get('title', 'N/A')}")
                            print(f"   - Handle: {product.get('handle', 'N/A')}")
                            print(f"   - URL: https://www.jamesavery.com/products/{product.get('handle', '')}")
                    else:
                        print("   No products found")
                except json.JSONDecodeError:
                    print("   Invalid JSON response")
            else:
                print("   No response from search")
                
            await asyncio.sleep(2)  # Wait between searches
        
        # Then try direct product URLs
        print("\n2. Testing direct URLs:")
        name_variations = [
            base_name,
            f"{base_name}-charm",
            base_name.replace(' ', '-'),
            f"{base_name.replace(' ', '-')}-charm"
        ]
        
        # Also try without certain common words
        skip_words = ['the', 'a', 'an']
        words = base_name.split()
        if len(words) > 1:
            filtered_name = ' '.join(word for word in words if word not in skip_words)
            name_variations.extend([
                filtered_name,
                filtered_name.replace(' ', '-'),
                f"{filtered_name}-charm",
                f"{filtered_name.replace(' ', '-')}-charm"
            ])
        
        # Clean up variations
        name_variations = list(set(
            re.sub(r'[^a-z0-9-&]', '', variation)
            for variation in name_variations
        ))
        
        for variation in name_variations:
            url = f"https://www.jamesavery.com/products/{variation}"
            print(f"\n   Trying URL: {url}")
            html = await scraper._make_request(url)
            
            if html:
                if 'product not found' not in html.lower():
                    print("   ✅ URL accessible!")
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Check title
                    title = soup.find('title')
                    if title:
                        print(f"   Page title: {title.text.strip()}")
                    
                    # Check for structured data
                    print("\n   Checking structured data:")
                    for script in soup.find_all('script', {'type': ['application/ld+json', 'application/json']}):
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict):
                                print("   Found structured data block:")
                                if 'image' in data:
                                    print(f"   - Has image field: {type(data['image'])}")
                                if 'images' in data:
                                    print(f"   - Has images field: {type(data['images'])}")
                                if 'offers' in data:
                                    print(f"   - Has offers field: {type(data['offers'])}")
                        except json.JSONDecodeError:
                            continue
                    
                    # Check for images
                    print("\n   Checking image elements:")
                    img_count = 0
                    for img in soup.find_all('img', {'src': re.compile(r'.*jamesavery.*')}):
                        img_count += 1
                        src = img.get('src', '')
                        cls = img.get('class', [])
                        print(f"   Image {img_count}:")
                        print(f"   - src: {src}")
                        print(f"   - class: {' '.join(cls)}")
                        
                        # Check other attributes
                        for attr in ['data-src', 'data-zoom-image', 'data-large']:
                            if img.has_attr(attr):
                                print(f"   - {attr}: {img[attr]}")
                    
                    if img_count == 0:
                        print("   No images found matching criteria")
                    
                    # Check meta tags
                    print("\n   Checking meta tags:")
                    for meta in soup.find_all('meta', {'property': ['og:image', 'product:image', 'og:price:amount', 'product:price:amount']}):
                        print(f"   - {meta.get('property', 'unknown')}: {meta.get('content', 'N/A')}")
                else:
                    print("   ❌ Product not found page")
            else:
                print("   ❌ No response")
            
            await asyncio.sleep(2)  # Wait between requests

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a charm name to debug")
        print("Example: python debug_charm.py 'Heart Charm'")
        sys.exit(1)
    
    charm_name = sys.argv[1]
    asyncio.run(debug_charm(charm_name))