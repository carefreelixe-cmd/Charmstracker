"""Quick test for eBay scraper only"""
from scrapers.scraperapi_client import ScraperAPIClient

print("🧪 Testing eBay Scraper with ScraperAPI\n")

scraper = ScraperAPIClient()
results = scraper.scrape_ebay('Jesus Loves Me Charm')

print(f"\n{'='*60}")
print(f"✅ SUCCESS: {len(results)} eBay listings found")
print(f"{'='*60}\n")

for i, item in enumerate(results[:10], 1):
    print(f"{i}. {item['title'][:70]}")
    print(f"   💰 ${item['price']}")
    print(f"   📦 {item['condition']}")
    print(f"   🖼️  {item['image_url'][:60]}...")
    print()
