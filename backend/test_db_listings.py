"""Check if listings are saved in database"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['charmstracker']

# Find charm with "Jesus Loves Me" in name
charm = db.charms.find_one({"name": {"$regex": "Jesus Loves Me", "$options": "i"}})

if not charm:
    print("❌ Charm not found in database")
    print("\n📋 Available charms:")
    all_charms = list(db.charms.find().limit(5))
    for c in all_charms:
        print(f"  - {c['name']} (ID: {c['_id']})")
else:
    print(f"\n✅ Found charm: {charm['name']}")
    print(f"   ID: {charm['_id']}")
    print(f"\n📊 Database Data:")
    print(f"   Listing Count: {charm.get('listing_count', 0)}")
    print(f"   Average Price: ${charm.get('average_price', 0)}")
    print(f"   Last Updated: {charm.get('last_updated', 'Never')}")
    print(f"   Images: {len(charm.get('images', []))}")
    
    listings = charm.get('listings', [])
    print(f"\n📦 Listings: {len(listings)} total")
    
    if listings:
        # Group by platform
        platforms = {}
        for listing in listings:
            platform = listing.get('platform', 'unknown')
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(listing)
        
        print("\n🔍 Breakdown by platform:")
        for platform, items in platforms.items():
            print(f"\n   {platform.upper()}: {len(items)} listings")
            # Show first listing sample
            if items:
                sample = items[0]
                print(f"     Sample: {sample.get('title', 'No title')[:60]}")
                print(f"     Price: ${sample.get('price', 0)}")
                print(f"     Image: {sample.get('image_url', 'No image')[:50]}...")
                print(f"     URL: {sample.get('url', 'No URL')[:50]}...")
        
        # Save full listings to JSON for inspection
        with open('db_listings_dump.json', 'w', encoding='utf-8') as f:
            json.dump(listings, f, indent=2)
        print(f"\n💾 Full listings saved to: db_listings_dump.json")
    else:
        print("   ⚠️ No listings found in database!")
        print("\n   This means either:")
        print("   1. Fetch Live Prices hasn't been clicked yet")
        print("   2. The scraper ran but failed to save data")
        print("   3. There's a database connection issue")
