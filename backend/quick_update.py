"""
Quick update script for James Avery charm data
"""
import asyncio
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin, quote_plus
import aiohttp
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def fetch_charm_from_james_avery(session, charm_name):
    """Fetch charm details from James Avery website"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # Try search API first
    search_query = quote_plus(f"{charm_name}")
    search_url = f"https://www.jamesavery.com/search?q={search_query}&type=product"
    
    try:
        async with session.get(search_url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for product grid
                product_grid = soup.find('div', {'class': ['product-grid', 'search-results-grid']})
                if not product_grid:
                    return None
                    
                # Find all product items
                products = product_grid.find_all('div', {'class': ['product', 'product-item']})
                
                best_match = None
                highest_score = 0
                
                search_words = set(charm_name.lower().replace('charm', '').split())
                
                for product in products:
                    # Get product title
                    title_elem = product.find(['h4', 'h3', 'div'], {'class': ['product-title', 'title']})
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip().lower()
                    title_words = set(title.split())
                    
                    # Calculate match score
                    score = len(search_words.intersection(title_words))
                    if 'charm' in title:
                        score += 1
                        
                    if score > highest_score:
                        # Get product URL
                        link = product.find('a', href=True)
                        if not link:
                            continue
                            
                        # Get product image
                        img = product.find('img', {'class': ['product-image', 'tile-image']})
                        if not img:
                            continue
                            
                        image_url = img.get('src', '')
                        if not image_url:
                            image_url = img.get('data-src', '')
                        
                        if image_url:
                            if image_url.startswith('//'):
                                image_url = 'https:' + image_url
                            
                            # Get high-res version if available
                            image_url = image_url.replace('_medium', '_large')
                            image_url = image_url.replace('_small', '_large')
                        
                        # Get price
                        price = None
                        price_elem = product.find(['span', 'div'], {'class': ['price', 'product-price']})
                        if price_elem:
                            price_text = price_elem.get_text().strip()
                            try:
                                price = float(re.sub(r'[^\d.]', '', price_text))
                            except ValueError:
                                pass
                        
                        best_match = {
                            'url': urljoin('https://www.jamesavery.com', link['href']),
                            'image': image_url,
                            'price': price,
                            'title': title
                        }
                        highest_score = score
                
                if best_match:
                    # Now fetch the full product page to get additional images
                    async with session.get(best_match['url'], headers=headers) as prod_response:
                        if prod_response.status == 200:
                            prod_html = await prod_response.text()
                            prod_soup = BeautifulSoup(prod_html, 'html.parser')
                            
                            # Get all product images
                            images = set()
                            images.add(best_match['image'])
                            
                            # Look in product gallery
                            gallery = prod_soup.find('div', {'class': ['product-gallery', 'gallery']})
                            if gallery:
                                for img in gallery.find_all('img'):
                                    src = img.get('src', '') or img.get('data-src', '')
                                    if src:
                                        if src.startswith('//'):
                                            src = 'https:' + src
                                        src = src.replace('_medium', '_large').replace('_small', '_large')
                                        images.add(src)
                            
                            best_match['images'] = list(images)
                            return best_match
    
    except Exception as e:
        print(f"Error fetching {charm_name}: {str(e)}")
        return None
    
    return None

async def quick_update():
    """Update charm data from James Avery website"""
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection details
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "charmtracker_production")
    
    # Create MongoDB client
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test database connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get all charms from database
        cursor = db.charms.find({})
        charms = await cursor.to_list(length=None)
        total_charms = len(charms)
        print(f"Found {total_charms} charms to update\n")
        
        updated_count = 0
        
        async with aiohttp.ClientSession() as session:
            for idx, charm in enumerate(charms, 1):
                print(f"\nProcessing [{idx}/{total_charms}] {charm['name']}")
                
                result = await fetch_charm_from_james_avery(session, charm['name'])
                
                if result:
                    # Update charm data
                    update_data = {
                        "james_avery_url": result['url'],
                        "james_avery_price": result['price'],
                        "images": result['images'],
                        "last_updated": datetime.utcnow()
                    }
                    
                    await db.charms.update_one(
                        {"_id": charm["_id"]},
                        {"$set": update_data}
                    )
                    
                    updated_count += 1
                    print(f"✅ Updated {charm['name']}")
                    print(f"   Price: ${result['price'] if result['price'] else 'N/A'}")
                    print(f"   Images: {len(result['images'])}")
                    print(f"   URL: {result['url']}")
                else:
                    print(f"❌ Could not find match for {charm['name']}")
                
                # Brief pause between requests
                await asyncio.sleep(2)
        
        print(f"\n✨ Update complete!")
        print(f"✅ Successfully updated {updated_count} out of {total_charms} charms")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(quick_update())