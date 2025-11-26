"""
Test scraper for "Jesus Loves Me Charm" to debug why charm details aren't showing
"""
import asyncio
import json
from scrapers.direct_scraper import DirectMarketplaceScraper
from scrapers.ebay_api_client import EbayAPIClient
from scrapers.james_avery_scraper import JamesAveryScraper
import os
from dotenv import load_dotenv

load_dotenv()

async def test_all_scrapers():
    """Test all scrapers for 'Jesus Loves Me Charm'"""
    
    charm_name = "Jesus Loves Me Charm"
    search_query = "James Avery Jesus Loves Me Charm"
    
    print("\n" + "="*80)
    print(f"TESTING ALL SCRAPERS FOR: {charm_name}")
    print("="*80 + "\n")
    
    # Test 1: Direct Scraper (AgentQL)
    print("\n" + "-"*80)
    print("1. TESTING DIRECT SCRAPER (AgentQL - Etsy, eBay, Poshmark)")
    print("-"*80)
    try:
        direct_scraper = DirectMarketplaceScraper()
        direct_results = await direct_scraper.scrape_all(search_query)
        
        print(f"\n✅ Direct Scraper returned {len(direct_results)} total listings")
        
        # Group by marketplace
        by_marketplace = {}
        for listing in direct_results:
            marketplace = listing.get('marketplace', 'unknown')
            if marketplace not in by_marketplace:
                by_marketplace[marketplace] = []
            by_marketplace[marketplace].append(listing)
        
        for marketplace, listings in by_marketplace.items():
            print(f"\n   📦 {marketplace.upper()}: {len(listings)} listings")
            for i, listing in enumerate(listings[:3], 1):  # Show first 3
                print(f"      {i}. {listing.get('title', 'No title')[:60]}")
                print(f"         Price: ${listing.get('price', 0)}")
                print(f"         URL: {listing.get('url', 'No URL')[:80]}")
                print(f"         Image: {listing.get('image_url', 'No image')[:80]}")
        
        # Save full results
        with open('test_direct_scraper_results.json', 'w', encoding='utf-8') as f:
            json.dump(direct_results, f, indent=2, default=str)
        print(f"\n   💾 Full results saved to: test_direct_scraper_results.json")
        
    except Exception as e:
        print(f"\n❌ Direct Scraper Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: eBay API Client
    print("\n" + "-"*80)
    print("2. TESTING EBAY API CLIENT")
    print("-"*80)
    try:
        ebay_client = EbayAPIClient()
        
        # Test active listings
        print("\n   Testing active listings...")
        active_listings = await ebay_client.search_listings(search_query)
        print(f"   ✅ Found {len(active_listings)} active eBay listings")
        for i, listing in enumerate(active_listings[:3], 1):
            print(f"      {i}. {listing.get('title', 'No title')[:60]}")
            print(f"         Price: ${listing.get('price', 0)}")
        
        # Test completed listings
        print("\n   Testing completed (sold) listings...")
        completed_listings = await ebay_client.search_completed_listings(search_query)
        print(f"   ✅ Found {len(completed_listings)} completed eBay listings")
        for i, listing in enumerate(completed_listings[:3], 1):
            print(f"      {i}. {listing.get('title', 'No title')[:60]}")
            print(f"         Price: ${listing.get('price', 0)}")
        
        # Save results
        ebay_results = {
            'active': active_listings,
            'completed': completed_listings
        }
        with open('test_ebay_results.json', 'w', encoding='utf-8') as f:
            json.dump(ebay_results, f, indent=2, default=str)
        print(f"\n   💾 Full results saved to: test_ebay_results.json")
        
    except Exception as e:
        print(f"\n❌ eBay API Client Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: James Avery Scraper
    print("\n" + "-"*80)
    print("3. TESTING JAMES AVERY SCRAPER")
    print("-"*80)
    try:
        ja_scraper = JamesAveryScraper()
        ja_results = await ja_scraper.search_charm(charm_name)
        
        if ja_results:
            print(f"\n   ✅ Found charm on James Avery website")
            print(f"      Name: {ja_results.get('name', 'No name')}")
            print(f"      Price: ${ja_results.get('price', 0)}")
            print(f"      URL: {ja_results.get('url', 'No URL')}")
            print(f"      Image: {ja_results.get('image_url', 'No image')}")
            print(f"      Description: {ja_results.get('description', 'No description')[:100]}")
            
            with open('test_james_avery_results.json', 'w', encoding='utf-8') as f:
                json.dump(ja_results, f, indent=2, default=str)
            print(f"\n   💾 Full results saved to: test_james_avery_results.json")
        else:
            print(f"\n   ⚠️  No results found on James Avery website")
            
    except Exception as e:
        print(f"\n❌ James Avery Scraper Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF ERRORS FROM note.txt:")
    print("="*80)
    print("""
    KEY ISSUES FOUND:
    
    1. ❌ eBay API Error:
       - Error: "Attempt to decode JSON with unexpected mimetype: text/plain"
       - Cause: eBay API is returning HTML error page instead of JSON
       - Impact: No eBay pricing data is being fetched
    
    2. ❌ James Avery SSL Error (sometimes):
       - Error: "[SSL: CERTIFICATE_VERIFY_FAILED]"
       - Cause: SSL certificate verification issues
       - Impact: James Avery product data may not load
    
    3. ⚠️  No listings found:
       - Many charms show "0 listings" from all marketplaces
       - This is why charm details page shows no data
    
    RECOMMENDATIONS:
    
    1. Fix eBay API credentials or use alternative eBay scraping method
    2. Add SSL verification bypass for James Avery scraper (or fix certificates)
    3. Improve search query matching for better results
    4. Add fallback to show charm even when no marketplace listings found
    """)
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_scrapers())
