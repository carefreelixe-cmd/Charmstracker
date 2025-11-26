"""
Test script to verify the AgentQL endpoint is working correctly
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_fetch_live_prices():
    """Test the fetch-live-prices endpoint"""
    
    # First, get a charm ID from the database
    print("🔍 Fetching charm list to get a test charm ID...")
    response = requests.get(f"{BASE_URL}/api/charms")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch charms: {response.status_code}")
        return
    
    charms = response.json()
    if not charms:
        print("❌ No charms found in database")
        return
    
    # Use the first charm
    test_charm = charms[0]
    charm_id = test_charm['_id']
    charm_name = test_charm['name']
    
    print(f"\n✅ Found test charm:")
    print(f"   ID: {charm_id}")
    print(f"   Name: {charm_name}\n")
    
    # Test the fetch-live-prices endpoint
    print(f"🤖 Testing AgentQL endpoint: POST /api/scraper/fetch-live-prices/{charm_id}")
    print(f"   This will scrape Etsy, eBay, and Poshmark for: {charm_name}\n")
    
    response = requests.post(f"{BASE_URL}/api/scraper/fetch-live-prices/{charm_id}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS! AgentQL scraping completed\n")
        print("📊 RESULTS:")
        print(f"   🎨 Etsy: {result['summary']['etsy']['count']} listings")
        print(f"   🛒 eBay: {result['summary']['ebay']['count']} listings")
        print(f"   👗 Poshmark: {result['summary']['poshmark']['count']} listings")
        print(f"   💰 Average Price: ${result['average_price']}")
        print(f"   📦 Total Listings: {result['total_listings']}\n")
        
        # Show sample listings
        if result['summary']['etsy']['listings']:
            print("Sample Etsy listings:")
            for listing in result['summary']['etsy']['listings'][:3]:
                print(f"   • {listing['title'][:60]}... - ${listing['price']}")
        
        return result
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


if __name__ == "__main__":
    print("🧪 Testing AgentQL API Endpoint Integration\n")
    print("="*60)
    test_fetch_live_prices()
    print("="*60)
