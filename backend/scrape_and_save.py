"""
Simple James Avery Scraper - Scrapes charms and saves to database
No duplicates - updates existing charms or creates new ones
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from scrapers.james_avery_scraper import JamesAveryScraper
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB
MONGO_URL = os.getenv('MONGO_URL', "mongodb://localhost:27017/")
DB_NAME = os.getenv('DB_NAME', "charmstracker")

async def scrape_and_save():
    """Scrape James Avery and save to database"""
    
    print("\n" + "="*70)
    print("🏪 JAMES AVERY SCRAPER - FRESH START")
    print("="*70 + "\n")
    
    # Connect to MongoDB
    print(f"📡 Connecting to MongoDB...")
    print(f"   Database: {DB_NAME}")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Test connection
    try:
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB!\n")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return
    
    # STEP 1: Clear all existing charms
    print("="*70)
    print("🗑️  STEP 1: Clearing all existing charms from database...")
    print("="*70)
    existing_count = await db.charms.count_documents({})
    print(f"Found {existing_count} existing charms")
    
    if existing_count > 0:
        result = await db.charms.delete_many({})
        print(f"✅ Deleted {result.deleted_count} charms\n")
    else:
        print("✅ Database already empty\n")
    
    scraper = JamesAveryScraper()
    
    try:
        # Get all product URLs
        print("="*70)
        print("🔍 STEP 2: Finding all products from James Avery...")
        print("="*70)
        product_urls = await scraper._get_all_product_urls()
        total = len(product_urls)
        print(f"✅ Found {total} products\n")
        
        if total == 0:
            print("❌ No products found!")
            return
        
        # Scrape and save
        print("="*70)
        print("📥 STEP 3: Scraping and saving (one-by-one)...")
        print("="*70)
        print("Each charm will be saved immediately after scraping.\n")
        
        saved = 0
        updated = 0
        failed = 0
        start = datetime.now()
        
        for i, url in enumerate(product_urls, 1):
            try:
                # Progress
                if i % 10 == 0 or i == 1:
                    elapsed = (datetime.now() - start).total_seconds()
                    if saved + updated > 0:
                        avg_time = elapsed / (saved + updated)
                        eta_min = int((avg_time * (total - i)) / 60)
                        print(f"[{i}/{total}] ETA: ~{eta_min} min | Saved: {saved} | Updated: {updated} | Failed: {failed}")
                    else:
                        print(f"[{i}/{total}]")
                
                # Scrape
                html = await scraper._make_request(url)
                if not html:
                    failed += 1
                    continue
                
                data = scraper._parse_product_page(html, url)
                if not data or not data.get('name'):
                    failed += 1
                    continue
                
                # Create charm document
                name = data['name']
                charm_id = f"charm_{name.lower().replace(' ', '_').replace('-', '_')}"
                
                # Format images to ensure they're high quality and displayable
                images = data.get('images', [])
                formatted_images = []
                for img_url in images:
                    # Ensure Scene7 images have proper size parameters
                    if 'scene7.com' in img_url and '?' not in img_url:
                        # Add size parameters for consistent high-quality display
                        img_url = f"{img_url}?wid=800&hei=800&fmt=jpeg&qlt=90"
                    formatted_images.append(img_url)
                
                charm = {
                    '_id': charm_id,
                    'id': charm_id,
                    'name': name,
                    'description': data.get('description', f"Beautiful {name} from James Avery"),
                    'price': data.get('price', data.get('official_price')),
                    'official_price': data.get('official_price'),
                    'material': data.get('material', 'Sterling Silver'),
                    'images': formatted_images,  # Use formatted images
                    'url': data.get('url', url),
                    'sku': data.get('sku'),
                    'status': data.get('status', 'Active'),
                    'is_retired': data.get('status') == 'Retired',
                    'avg_price': data.get('price', data.get('official_price', 50)),
                    
                    # Price changes (initialize to 0)
                    'price_change_7d': 0.0,
                    'price_change_30d': 0.0,
                    'price_change_90d': 0.0,
                    
                    # Popularity (random for now)
                    'popularity': 75,
                    
                    'listings': [],
                    'price_history': [],
                    'related_charm_ids': [],
                    'scraped_at': datetime.now(),
                    'created_at': datetime.now(),
                    'last_updated': datetime.now()
                }
                
                # Check if exists
                existing = await db.charms.find_one({'_id': charm_id})
                
                if existing:
                    # Update existing
                    await db.charms.update_one(
                        {'_id': charm_id},
                        {'$set': {
                            'name': charm['name'],
                            'description': charm['description'],
                            'price': charm['price'],
                            'official_price': charm['official_price'],
                            'material': charm['material'],
                            'images': charm['images'],
                            'url': charm['url'],
                            'sku': charm['sku'],
                            'status': charm['status'],
                            'is_retired': charm['is_retired'],
                            'scraped_at': charm['scraped_at'],
                            'last_updated': charm['last_updated']
                        }}
                    )
                    updated += 1
                    if i % 10 == 0:
                        print(f"  ✏️  Updated: {name}")
                else:
                    # Insert new
                    await db.charms.insert_one(charm)
                    saved += 1
                    if i % 10 == 0:
                        print(f"  ✅ Saved: {name}")
                
                # Show details every 50
                if i % 50 == 0:
                    price_display = f"${charm['price']}" if charm['price'] else "N/A"
                    img_count = len(charm['images'])
                    print(f"     💰 {price_display} | 📷 {img_count} images")
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                failed += 1
                if i % 50 == 0:
                    print(f"  ❌ Error: {str(e)[:50]}")
                continue
        
        # Summary
        total_time = int((datetime.now() - start).total_seconds() / 60)
        
        print("\n" + "="*70)
        print("📊 COMPLETE!")
        print("="*70)
        print(f"✅ New charms saved: {saved}")
        print(f"✏️  Existing updated: {updated}")
        print(f"❌ Failed: {failed}")
        print(f"📦 Total in database: {await db.charms.count_documents({})}")
        print(f"⏱️  Time taken: {total_time} minutes")
        print("="*70 + "\n")
        
        # Show samples
        if saved > 0 or updated > 0:
            print("📝 Sample charms:")
            samples = await db.charms.find({}).sort('scraped_at', -1).limit(5).to_list(5)
            for idx, c in enumerate(samples, 1):
                price = f"${c.get('price', c.get('official_price', 'N/A'))}"
                imgs = len(c.get('images', []))
                print(f"  {idx}. {c['name']} - {price} ({imgs} images)")
            print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted!")
        print(f"✅ Saved: {saved} | ✏️  Updated: {updated} | ❌ Failed: {failed}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if hasattr(scraper, 'session') and scraper.session:
            await scraper.session.close()
        client.close()

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║      James Avery Scraper - No Duplicates              ║
    ║                                                        ║
    ║  • Scrapes all charms from James Avery website        ║
    ║  • Gets: name, price, images, description, SKU        ║
    ║  • Saves to MongoDB (updates if exists)               ║
    ║  • No duplicates - safe to run multiple times         ║
    ║                                                        ║
    ║  ⏱️  Estimated time: 30-45 minutes                     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(scrape_and_save())
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(0)
