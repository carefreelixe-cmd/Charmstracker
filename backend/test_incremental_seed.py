"""
Quick test of incremental seeding - scrapes just 3 charms
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from scrapers.james_avery_scraper import JamesAveryScraper
from datetime import datetime

MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "charmstracker"

async def test_seed():
    """Test seeding with just 3 products"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    scraper = JamesAveryScraper()
    
    try:
        print("\n🔍 Step 1: Discovering product URLs...")
        product_urls = await scraper._get_all_product_urls()
        
        print(f"✅ Found {len(product_urls)} total products")
        print(f"📥 Testing with first 3 products...\n")
        
        test_urls = list(product_urls)[:3]
        
        for idx, url in enumerate(test_urls, 1):
            print(f"[{idx}/3] Scraping: {url}")
            
            html = await scraper._make_request(url)
            if not html:
                print("  ❌ Failed to fetch")
                continue
            
            charm_data = scraper._parse_product_page(html, url)
            if not charm_data:
                print("  ❌ Failed to parse")
                continue
            
            name = charm_data.get('name', 'Unknown')
            price = charm_data.get('price', charm_data.get('official_price', 'N/A'))
            images = len(charm_data.get('images', []))
            
            print(f"  ✅ {name}")
            print(f"     💰 ${price}")
            print(f"     📷 {images} images")
            
            # Create document
            charm_id = f"test_{name.lower().replace(' ', '_')}"
            charm_data['_id'] = charm_id
            charm_data['id'] = charm_id
            charm_data['scraped_at'] = datetime.utcnow()
            
            # Save to temp collection
            await db.test_charms.insert_one(charm_data)
            print(f"     💾 Saved to test_charms collection\n")
            
            await asyncio.sleep(0.5)
        
        print("✅ Test complete!")
        print(f"📊 Check database: {DB_NAME}.test_charms")
        
        # Show what was saved
        count = await db.test_charms.count_documents({})
        print(f"💾 Total saved: {count} charms")
        
    finally:
        # Close session if it exists
        if hasattr(scraper, 'session') and scraper.session:
            await scraper.session.close()
        client.close()

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║         Quick Test - Incremental Seeding            ║
    ║                                                      ║
    ║  This will scrape just 3 charms as a test.          ║
    ║  Saves to 'test_charms' collection (not 'charms').  ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(test_seed())
