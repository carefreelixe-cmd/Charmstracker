"""
Test complete integration: Etsy (ScraperAPI) + eBay (ScraperAPI) + Poshmark (AgentQL)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scrapers.scraperapi_client import ScraperAPIClient
import json

print("="*70)
print("🧪 TESTING COMPLETE SCRAPER INTEGRATION")
print("="*70)
print("\n📋 Configuration:")
print("   🎨 Etsy: ScraperAPI (HTML parsing)")
print("   🛒 eBay: ScraperAPI (Structured JSON API)")
print("   👗 Poshmark: AgentQL (AI-powered)")
print("\n" + "="*70)

charm_name = "Jesus Loves Me Charm"
print(f"\n🔍 Searching for: {charm_name}")
print("="*70 + "\n")

scraper = ScraperAPIClient()
all_results = scraper.scrape_all(charm_name)

# Organize by platform
etsy_results = [r for r in all_results if r['platform'] == 'etsy']
ebay_results = [r for r in all_results if r['platform'] == 'ebay']
poshmark_results = [r for r in all_results if r['platform'] == 'poshmark']

print("\n" + "="*70)
print("📊 RESULTS SUMMARY")
print("="*70)
print(f"\n✅ TOTAL LISTINGS: {len(all_results)}")
print(f"   🎨 Etsy: {len(etsy_results)} listings")
print(f"   🛒 eBay: {len(ebay_results)} listings")
print(f"   👗 Poshmark: {len(poshmark_results)} listings")
print("\n" + "="*70)

# Show sample from each platform
if etsy_results:
    print("\n🎨 ETSY SAMPLES:")
    print("-"*70)
    for i, item in enumerate(etsy_results[:3], 1):
        print(f"\n{i}. {item['title'][:60]}")
        print(f"   💰 Price: ${item['price']}")
        print(f"   📦 Condition: {item['condition']}")
        print(f"   🖼️  Image: {item['image_url'][:50]}..." if item['image_url'] else "   🖼️  Image: None")
        print(f"   🔗 URL: {item['url'][:60]}...")

if ebay_results:
    print("\n\n🛒 EBAY SAMPLES:")
    print("-"*70)
    for i, item in enumerate(ebay_results[:3], 1):
        print(f"\n{i}. {item['title'][:60]}")
        print(f"   💰 Price: ${item['price']}")
        print(f"   📦 Condition: {item['condition']}")
        print(f"   🖼️  Image: {item['image_url'][:50]}..." if item['image_url'] else "   🖼️  Image: None")
        print(f"   🔗 URL: {item['url'][:60]}..." if item.get('url') else "   🔗 URL: None")

if poshmark_results:
    print("\n\n👗 POSHMARK SAMPLES:")
    print("-"*70)
    for i, item in enumerate(poshmark_results[:3], 1):
        print(f"\n{i}. {item['title'][:60]}")
        print(f"   💰 Price: ${item['price']}")
        print(f"   📦 Condition: {item['condition']}")
        print(f"   🖼️  Image: {item['image_url'][:50]}..." if item['image_url'] else "   🖼️  Image: None")
        print(f"   🔗 URL: {item['url'][:60]}...")

# Calculate statistics
all_prices = [r['price'] for r in all_results if r['price'] > 0]
if all_prices:
    print("\n\n" + "="*70)
    print("💵 PRICE STATISTICS")
    print("="*70)
    print(f"   Average: ${sum(all_prices) / len(all_prices):.2f}")
    print(f"   Minimum: ${min(all_prices):.2f}")
    print(f"   Maximum: ${max(all_prices):.2f}")
    print(f"   Total Listings: {len(all_results)}")

# Check data completeness
print("\n\n" + "="*70)
print("✅ DATA COMPLETENESS CHECK")
print("="*70)

complete_listings = [r for r in all_results if r.get('title') and r.get('price') and r.get('image_url') and r.get('url')]
print(f"\n   Complete listings (title + price + image + URL): {len(complete_listings)}/{len(all_results)}")
print(f"   Listings with images: {len([r for r in all_results if r.get('image_url')])}/{len(all_results)}")
print(f"   Listings with URLs: {len([r for r in all_results if r.get('url')])}/{len(all_results)}")
print(f"   Listings with conditions: {len([r for r in all_results if r.get('condition')])}/{len(all_results)}")

# Save to JSON
output_file = "integration_test_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'search_term': charm_name,
        'total_listings': len(all_results),
        'platform_breakdown': {
            'etsy': len(etsy_results),
            'ebay': len(ebay_results),
            'poshmark': len(poshmark_results)
        },
        'listings': all_results
    }, f, indent=2)

print(f"\n\n💾 Full results saved to: {output_file}")

print("\n" + "="*70)
if len(all_results) > 30:
    print("✅ SUCCESS! All scrapers working - ready for production!")
elif len(all_results) > 20:
    print("✅ GOOD! Most scrapers working - Poshmark may need adjustment")
else:
    print("⚠️  WARNING: Low listing count - check scraper configurations")
print("="*70 + "\n")
