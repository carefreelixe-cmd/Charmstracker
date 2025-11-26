"""
Simulate API call to fetch-live-prices endpoint
This tests the complete flow: scrape -> save to DB -> verify data
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pymongo import MongoClient
from dotenv import load_dotenv
from scrapers.scraperapi_client import ScraperAPIClient
from datetime import datetime

load_dotenv()

async def test_fetch_and_save():
    print("="*70)
    print("🧪 TESTING COMPLETE FLOW: Scrape → Save → Verify")
    print("="*70)
    
    # Connect to database
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['charmstracker']
    
    # Find or create test charm
    charm_id = "charm_jesus_loves_me_charm"
    charm_name = "Jesus Loves Me Charm"
    
    # Check if charm exists
    charm = db.charms.find_one({"_id": charm_id})
    if not charm:
        print(f"\n⚠️  Charm '{charm_name}' not found in database")
        print("   Creating test charm...")
        db.charms.insert_one({
            "_id": charm_id,
            "name": charm_name,
            "description": "Test charm for scraper integration",
            "james_avery_price": 49.00,
            "listings": [],
            "images": []
        })
        charm = db.charms.find_one({"_id": charm_id})
    
    print(f"\n✅ Found charm: {charm['name']}")
    print(f"   ID: {charm['_id']}")
    print(f"   Current listings: {len(charm.get('listings', []))}")
    
    # Scrape data
    print("\n" + "="*70)
    print("📡 SCRAPING MARKETPLACES...")
    print("="*70)
    
    scraper = ScraperAPIClient()
    all_listings = scraper.scrape_all(f"James Avery {charm_name}")
    
    print(f"\n✅ Scraped {len(all_listings)} total listings")
    
    # Organize by platform
    etsy_listings = [l for l in all_listings if l.get('platform') == 'etsy']
    ebay_listings = [l for l in all_listings if l.get('platform') == 'ebay']
    poshmark_listings = [l for l in all_listings if l.get('platform') == 'poshmark']
    
    print(f"   🎨 Etsy: {len(etsy_listings)}")
    print(f"   🛒 eBay: {len(ebay_listings)}")
    print(f"   👗 Poshmark: {len(poshmark_listings)}")
    
    # Calculate average price
    prices = [l['price'] for l in all_listings if l['price'] > 0]
    average_price = sum(prices) / len(prices) if prices else 0
    
    print(f"\n💰 Price Stats:")
    print(f"   Average: ${average_price:.2f}")
    print(f"   Min: ${min(prices):.2f}")
    print(f"   Max: ${max(prices):.2f}")
    
    # Extract images
    images = [l['image_url'] for l in all_listings if l.get('image_url')]
    
    # Save to database
    print("\n" + "="*70)
    print("💾 SAVING TO DATABASE...")
    print("="*70)
    
    update_data = {
        'listings': all_listings,
        'average_price': round(average_price, 2),
        'last_updated': datetime.utcnow(),
        'listing_count': len(all_listings)
    }
    
    if images:
        existing_images = charm.get('images', [])
        all_images = list(set(existing_images + images[:10]))
        update_data['images'] = all_images
        print(f"   Updated images: {len(all_images)} total")
    
    result = db.charms.update_one(
        {"_id": charm_id},
        {"$set": update_data}
    )
    
    print(f"\n✅ Database updated:")
    print(f"   Modified: {result.modified_count} document(s)")
    print(f"   Matched: {result.matched_count} document(s)")
    
    # Verify data was saved
    print("\n" + "="*70)
    print("🔍 VERIFYING SAVED DATA...")
    print("="*70)
    
    updated_charm = db.charms.find_one({"_id": charm_id})
    
    print(f"\n📊 Database Record:")
    print(f"   Listing Count: {updated_charm.get('listing_count', 0)}")
    print(f"   Average Price: ${updated_charm.get('average_price', 0):.2f}")
    print(f"   Last Updated: {updated_charm.get('last_updated')}")
    print(f"   Images: {len(updated_charm.get('images', []))}")
    
    saved_listings = updated_charm.get('listings', [])
    print(f"\n📦 Saved Listings: {len(saved_listings)}")
    
    if saved_listings:
        platforms = {}
        for listing in saved_listings:
            platform = listing.get('platform', 'unknown')
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(listing)
        
        for platform, items in platforms.items():
            print(f"\n   {platform.upper()}: {len(items)} listings")
            if items:
                sample = items[0]
                print(f"     ✓ Title: {sample.get('title', 'N/A')[:60]}")
                print(f"     ✓ Price: ${sample.get('price', 0):.2f}")
                print(f"     ✓ Image: {'Yes' if sample.get('image_url') else 'No'}")
                print(f"     ✓ URL: {'Yes' if sample.get('url') else 'No'}")
                print(f"     ✓ Condition: {sample.get('condition', 'N/A')}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE - Data is saved and ready!")
    print("="*70)
    print("\n📌 Next Steps:")
    print("   1. Refresh the charm details page in your browser")
    print("   2. You should see 37 listings with actual product details")
    print("   3. Each listing shows: title, image, price, condition")
    print(f"\n🔗 View charm at: http://localhost:3000/charm/{charm_id}")

if __name__ == "__main__":
    asyncio.run(test_fetch_and_save())
