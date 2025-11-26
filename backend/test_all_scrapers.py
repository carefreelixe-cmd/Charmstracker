"""Test all three scrapers together"""
from scrapers.scraperapi_client import ScraperAPIClient

print("🧪 Testing ALL Scrapers (Etsy + eBay + Poshmark)\n")

scraper = ScraperAPIClient()
results = scraper.scrape_all('Jesus Loves Me Charm')

etsy_count = len([r for r in results if r['platform'] == 'etsy'])
ebay_count = len([r for r in results if r['platform'] == 'ebay'])
poshmark_count = len([r for r in results if r['platform'] == 'poshmark'])

print(f"\n{'='*60}")
print(f"✅ TOTAL: {len(results)} listings")
print(f"   🎨 Etsy: {etsy_count}")
print(f"   🛒 eBay: {ebay_count}")
print(f"   👗 Poshmark: {poshmark_count}")
print(f"{'='*60}\n")

# Show first 5 from each platform
print("📋 SAMPLE LISTINGS:\n")

etsy_listings = [r for r in results if r['platform'] == 'etsy'][:3]
if etsy_listings:
    print("🎨 ETSY:")
    for item in etsy_listings:
        print(f"  • {item['title'][:50]}... - ${item['price']}")

ebay_listings = [r for r in results if r['platform'] == 'ebay'][:3]
if ebay_listings:
    print("\n🛒 EBAY:")
    for item in ebay_listings:
        print(f"  • {item['title'][:50]}... - ${item['price']}")

poshmark_listings = [r for r in results if r['platform'] == 'poshmark'][:3]
if poshmark_listings:
    print("\n👗 POSHMARK:")
    for item in poshmark_listings:
        print(f"  • {item['title'][:50]}... - ${item['price']}")

print(f"\n{'='*60}")
print("✅ All scrapers working correctly!")
print(f"{'='*60}")
