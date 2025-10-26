"""
Test eBay API Connection and Scraping
"""

import asyncio
import os
from dotenv import load_dotenv
from scrapers.ebay_scraper import ebay_scraper

load_dotenv()

async def test_ebay():
    print("=" * 80)
    print("🧪 TESTING EBAY API/SCRAPER")
    print("=" * 80)
    print()
    
    # Check credentials
    app_id = os.getenv('EBAY_APP_ID', '')
    print(f"🔑 eBay App ID: {app_id[:30]}..." if app_id else "❌ No eBay App ID found!")
    print(f"🌍 Environment: {'SANDBOX (SBX)' if 'SBX' in app_id else 'PRODUCTION'}")
    print()
    
    # Test search
    test_charms = ["bow", "heart", "cross"]
    
    for charm_name in test_charms:
        print(f"\n{'='*80}")
        print(f"🔍 Testing: {charm_name.upper()} CHARM")
        print(f"{'='*80}")
        
        result = await ebay_scraper.search_charm(charm_name, limit=5)
        
        listings = result.get('listings', [])
        avg_price = result.get('avg_price')
        
        print(f"\n📊 RESULTS:")
        print(f"   Listings Found: {len(listings)}")
        print(f"   Average Price: ${avg_price}" if avg_price else "   Average Price: N/A")
        
        if listings:
            print(f"\n📋 TOP 3 LISTINGS:")
            for idx, listing in enumerate(listings[:3], 1):
                print(f"   {idx}. ${listing['price']:.2f} - {listing['title'][:60]}")
                print(f"      Platform: {listing['platform']}")
                print(f"      Condition: {listing['condition']}")
                print(f"      URL: {listing['url'][:70]}...")
                print()
        else:
            print(f"\n⚠️  No listings found")
        
        # Wait between searches
        await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_ebay())
