"""
Test script to verify eBay pricing fix
Run with: python test_ebay_fix.py
"""

import asyncio
from scrapers.ebay_scraper import ebay_scraper

async def test_ebay_scraper():
    """Test that eBay scraper returns correct format"""
    print("🧪 Testing eBay Scraper Fix\n")
    
    test_charms = [
        "Heart Charm",
        "Cross Charm",
        "NonExistentCharm12345"  # Should return empty but not crash
    ]
    
    for charm_name in test_charms:
        print(f"📦 Testing: {charm_name}")
        print("-" * 60)
        
        try:
            result = await ebay_scraper.search_charm(charm_name, limit=5)
            
            # Check return type
            if isinstance(result, dict):
                print("✅ Returns dict (correct format)")
                print(f"   - Has 'listings' key: {'listings' in result}")
                print(f"   - Has 'avg_price' key: {'avg_price' in result}")
                
                listings = result.get('listings', [])
                avg_price = result.get('avg_price')
                
                print(f"   - Listings count: {len(listings)}")
                print(f"   - Average price: ${avg_price if avg_price else 'N/A'}")
                
                if listings:
                    print(f"\n   First listing:")
                    first = listings[0]
                    print(f"   - Platform: {first.get('platform')}")
                    print(f"   - Price: ${first.get('price', 0):.2f}")
                    print(f"   - Title: {first.get('title', 'N/A')[:50]}...")
                else:
                    print("   ⚠️  No listings found")
                    
            elif isinstance(result, list):
                print("❌ Returns list (OLD format - needs fix)")
                print(f"   - Count: {len(result)}")
            else:
                print(f"❌ Returns unknown type: {type(result)}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_ebay_scraper())
