import requests
import json

# Test API endpoint
url = "http://localhost:8000/api/charms/charm_jesus_loves_me_charm"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"✅ API Response received")
    print(f"   Charm: {data.get('name', 'Unknown')}")
    print(f"   Listings count: {len(data.get('listings', []))}")
    
    if data.get('listings'):
        listing = data['listings'][0]
        print(f"\n📦 First Listing:")
        print(f"   Title: {listing.get('title', 'NO TITLE')}")
        print(f"   Price: ${listing.get('price', 0)}")
        print(f"   Image URL: {listing.get('image_url', 'NO IMAGE')[:60]}...")
        print(f"   Condition: {listing.get('condition', 'NO CONDITION')}")
        print(f"   Platform: {listing.get('platform', 'NO PLATFORM')}")
else:
    print(f"❌ API Error: {response.status_code}")
