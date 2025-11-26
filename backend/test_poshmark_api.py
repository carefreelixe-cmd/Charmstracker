"""
Test Poshmark Apify API
Check if the API is returning data
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Poshmark scraper
from scrapers.poshmark_scraper import poshmark_scraper

async def test_poshmark():
    """Test Poshmark API with a simple search"""
    
    print("=" * 60)
    print("🧪 TESTING POSHMARK APIFY API")
    print("=" * 60)
    
    # Check if API token is configured
    api_token = os.getenv('APIFY_API_TOKEN', '')
    actor_id = os.getenv('APIFY_POSHMARK_ACTOR_ID', '')
    
    print(f"\n📋 Configuration:")
    print(f"   API Token: {api_token[:20]}..." if api_token else "   API Token: NOT SET")
    print(f"   Actor ID: {actor_id}")
    
    if not api_token or api_token == 'your_apify_token_here':
        print("\n❌ ERROR: Apify API token not configured!")
        print("   Set APIFY_API_TOKEN in backend/.env file")
        return
    
    # Test search
    test_charm = "James Avery Cross"
    print(f"\n🔍 Testing search for: {test_charm}")
    print("-" * 60)
    
    try:
        # Call the scraper
        results = await poshmark_scraper.search_charm(test_charm, limit=5)
        
        print(f"\n✅ API Response Received!")
        print(f"📦 Total Results: {len(results)}")
        
        if results:
            print(f"\n📊 Sample Listings:")
            for i, listing in enumerate(results[:3], 1):
                print(f"\n   Listing {i}:")
                print(f"      Platform: {listing.get('platform', 'N/A')}")
                print(f"      Title: {listing.get('title', 'N/A')[:60]}...")
                print(f"      Price: ${listing.get('price', 0):.2f}")
                print(f"      Condition: {listing.get('condition', 'N/A')}")
                print(f"      URL: {listing.get('url', 'N/A')[:60]}...")
                print(f"      Seller: {listing.get('seller', 'N/A')}")
        else:
            print("\n⚠️  No results found!")
            print("   Possible reasons:")
            print("   - No Poshmark listings for this charm")
            print("   - Apify actor might be processing")
            print("   - API rate limit reached")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_poshmark())
