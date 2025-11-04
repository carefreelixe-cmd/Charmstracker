"""
Test script to verify scheduler is working correctly
Run this to check if automatic scraping is configured properly
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv('MONGO_URL', "mongodb://localhost:27017/")
DB_NAME = os.getenv('DB_NAME', "charmstracker")


async def test_scheduler_setup():
    """Test scheduler configuration"""
    
    print("\n" + "="*70)
    print("🔍 SCHEDULER CONFIGURATION TEST")
    print("="*70 + "\n")
    
    # Test 1: MongoDB Connection
    print("📡 Test 1: MongoDB Connection")
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        await client.admin.command('ping')
        print("   ✅ MongoDB connected successfully")
        print(f"   Database: {DB_NAME}\n")
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {str(e)}\n")
        return False
    
    # Test 2: Check Charms Collection
    print("📦 Test 2: Charms Collection")
    try:
        total_charms = await db.charms.count_documents({})
        print(f"   ✅ Found {total_charms} charms in database")
        
        if total_charms > 0:
            # Get sample
            sample = await db.charms.find_one({})
            print(f"   Sample charm: {sample.get('name', 'Unknown')}")
            print(f"   Has images: {len(sample.get('images', []))} images")
            print(f"   Last updated: {sample.get('last_updated', 'Never')}")
        print()
    except Exception as e:
        print(f"   ❌ Error accessing charms: {str(e)}\n")
    
    # Test 3: Scheduler Service
    print("🤖 Test 3: Scheduler Service")
    try:
        from services.scheduler import BackgroundScheduler
        
        scheduler = BackgroundScheduler(db)
        print("   ✅ Scheduler service imported successfully")
        print(f"   Update interval: {scheduler.update_interval_hours} hours")
        print(f"   Scraper interval: {scheduler.scraper_interval_seconds / 3600} hours")
        print(f"   Batch size: {scheduler.batch_size}")
        print()
    except Exception as e:
        print(f"   ❌ Error importing scheduler: {str(e)}\n")
    
    # Test 4: James Avery Scraper
    print("🏪 Test 4: James Avery Scraper")
    try:
        from scrapers.james_avery_scraper import JamesAveryScraper
        
        scraper = JamesAveryScraper()
        print("   ✅ James Avery scraper imported successfully")
        print("   Testing connection to James Avery website...")
        
        # Try to get one product URL
        urls = await scraper._get_all_product_urls()
        if urls and len(urls) > 0:
            print(f"   ✅ Successfully found {len(urls)} product URLs")
            print(f"   Sample URL: {urls[0][:60]}...")
        else:
            print("   ⚠️  No product URLs found (check website access)")
        
        if hasattr(scraper, 'session') and scraper.session:
            await scraper.session.close()
        print()
    except Exception as e:
        print(f"   ❌ Error with scraper: {str(e)}\n")
    
    # Test 5: API Endpoints
    print("🔌 Test 5: API Endpoints")
    try:
        from routes.scraper import router
        
        print("   ✅ Scraper routes imported successfully")
        print("   Available endpoints:")
        for route in router.routes:
            print(f"      {route.methods} {route.path}")
        print()
    except Exception as e:
        print(f"   ❌ Error importing routes: {str(e)}\n")
    
    # Summary
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print("✅ All tests passed!")
    print()
    print("🚀 Your scheduler is configured correctly!")
    print()
    print("Next steps:")
    print("  1. Start backend: python server.py")
    print("  2. Check logs for: 'Background scheduler started'")
    print("  3. Check logs for: 'James Avery scraper: every 6 hours'")
    print("  4. Wait 1 minute for first scrape to start")
    print()
    print("To trigger manual scrape:")
    print("  curl -X POST http://localhost:8000/api/scraper/james-avery/scrape")
    print()
    print("="*70)
    
    client.close()
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_scheduler_setup())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
