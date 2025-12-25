"""
Quick test script to verify scrapers are working
Run this on the server to debug why fetch-live-prices returns 0 listings
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraperapi_client import ScraperAPIClient
import json

print("="*70)
print("TESTING SCRAPERAPI CLIENT - LIVE PRICES")
print("="*70)
print()

# Test with a simple charm name
charm_name = "Jesus Loves Me Charm"
full_query = f"James Avery {charm_name}"

print(f"🔍 Testing with: {full_query}")
print()

scraper = ScraperAPIClient()

print("\n📊 SCRAPING ALL PLATFORMS...")
print("-"*70)

all_listings = scraper.scrape_all(full_query)

print("\n" + "="*70)
print(f"RESULTS: {len(all_listings)} TOTAL LISTINGS")
print("="*70)
print()

if all_listings:
    # Group by platform
    etsy_listings = [l for l in all_listings if l['platform'] == 'etsy']
    ebay_listings = [l for l in all_listings if l['platform'] == 'ebay']
    poshmark_listings = [l for l in all_listings if l['platform'] == 'poshmark']
    
    print(f"🎨 Etsy: {len(etsy_listings)} listings")
    if etsy_listings:
        print(f"   Sample: {etsy_listings[0]['title'][:60]} - ${etsy_listings[0]['price']}")
    print()
    
    print(f"🛒 eBay: {len(ebay_listings)} listings")
    if ebay_listings:
        print(f"   Sample: {ebay_listings[0]['title'][:60]} - ${ebay_listings[0]['price']}")
    print()
    
    print(f"👗 Poshmark: {len(poshmark_listings)} listings")
    if poshmark_listings:
        print(f"   Sample: {poshmark_listings[0]['title'][:60]} - ${poshmark_listings[0]['price']}")
    print()
    
    # Calculate average
    prices = [l['price'] for l in all_listings if l['price'] > 0]
    if prices:
        avg_price = sum(prices) / len(prices)
        print(f"💰 Average Price: ${avg_price:.2f}")
        print(f"💰 Min Price: ${min(prices):.2f}")
        print(f"💰 Max Price: ${max(prices):.2f}")
    
    # Save results
    output_file = 'test_scraper_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'charm_name': charm_name,
            'query': full_query,
            'total_listings': len(all_listings),
            'etsy_count': len(etsy_listings),
            'ebay_count': len(ebay_listings),
            'poshmark_count': len(poshmark_listings),
            'average_price': avg_price if prices else 0,
            'listings': all_listings
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
else:
    print("❌ NO LISTINGS FOUND!")
    print()
    print("Possible reasons:")
    print("1. ScraperAPI key is invalid or out of credits")
    print("2. Search query is not finding results")
    print("3. HTML structure changed and selectors need updating")
    print("4. AgentQL API key missing (for Poshmark)")
    print()
    print("Next steps:")
    print("1. Check ScraperAPI dashboard: https://dashboard.scraperapi.com")
    print("2. Verify AGENTQL_API_KEY in .env file")
    print("3. Check backend logs for errors")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)
