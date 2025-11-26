"""
Test ScraperAPI for James Avery "Jesus Loves Me Charm"
This will show what data is returned and help debug the charm details page
"""
from scrapers.scraperapi_client import ScraperAPIClient
import json

def test_scraperapi_james_avery():
    """Test ScraperAPI with Jesus Loves Me Charm"""
    
    charm_name = "James Avery Jesus Loves Me Charm"
    
    print("\n" + "="*80)
    print(f"🧪 TESTING SCRAPERAPI FOR: {charm_name}")
    print("="*80 + "\n")
    
    print("⚙️  Configuration:")
    print("   - Using ScraperAPI (bypasses bot detection)")
    print("   - API Key: 0afc0ab6e056e61161c0097ebbb5231a")
    print("   - Will scrape: Etsy, eBay, Poshmark")
    print("   - JavaScript rendering: ENABLED")
    print("\n" + "-"*80 + "\n")
    
    try:
        # Create scraper
        scraper = ScraperAPIClient()
        
        print("🎯 Starting scraping process...\n")
        
        # Scrape all marketplaces
        results = scraper.scrape_all(charm_name)
        
        # Print summary
        print("\n" + "="*80)
        print("📊 RESULTS SUMMARY")
        print("="*80 + "\n")
        
        if not results:
            print("❌ NO RESULTS FOUND!")
            print("\nPossible reasons:")
            print("  1. ScraperAPI couldn't find matching listings")
            print("  2. Search query didn't match any products")
            print("  3. HTML structure has changed on the websites")
            print("  4. ScraperAPI rate limit reached")
            
            print("\n💡 Try these fixes:")
            print("  1. Test with a more generic search: 'James Avery charm'")
            print("  2. Check ScraperAPI dashboard for usage")
            print("  3. Verify the API key is valid")
            return
        
        # Group by platform
        by_platform = {
            'etsy': [],
            'ebay': [],
            'poshmark': []
        }
        
        for listing in results:
            platform = listing.get('platform', 'unknown')
            if platform in by_platform:
                by_platform[platform].append(listing)
        
        # Print detailed results
        for platform, listings in by_platform.items():
            if not listings:
                continue
                
            print(f"\n{'='*60}")
            print(f"🏪 {platform.upper()} - {len(listings)} listings")
            print(f"{'='*60}")
            
            for i, listing in enumerate(listings, 1):
                print(f"\n  {i}. {listing.get('title', 'No title')[:70]}")
                print(f"     💰 Price: ${listing.get('price', 0)}")
                print(f"     📦 Condition: {listing.get('condition', 'Unknown')}")
                print(f"     🔗 URL: {listing.get('url', 'No URL')[:70]}")
                if listing.get('image_url'):
                    print(f"     🖼️  Image: {listing['image_url'][:70]}")
        
        # Calculate statistics
        prices = [l['price'] for l in results if l.get('price', 0) > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"\n{'='*60}")
            print(f"💵 PRICE STATISTICS")
            print(f"{'='*60}")
            print(f"   Average: ${avg_price:.2f}")
            print(f"   Minimum: ${min(prices):.2f}")
            print(f"   Maximum: ${max(prices):.2f}")
            print(f"   Total listings: {len(results)}")
            print(f"{'='*60}")
        
        # Save to file
        output_file = 'test_scraperapi_james_avery_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        # Show what will be saved to database
        print("\n" + "="*80)
        print("💾 DATABASE UPDATE PREVIEW")
        print("="*80)
        print(f"""
This data will be saved when user clicks "Fetch Live Data":

- Charm Name: {charm_name}
- Listings Found: {len(results)}
- Average Price: ${avg_price:.2f if prices else 0}
- Etsy Listings: {len(by_platform['etsy'])}
- eBay Listings: {len(by_platform['ebay'])}
- Poshmark Listings: {len(by_platform['poshmark'])}
- Images Found: {len([l for l in results if l.get('image_url')])}

The charm details page will show:
✓ Average price from all platforms
✓ Individual listings with prices
✓ Links to each marketplace
✓ Product images
✓ Condition information
        """)
        
        print("="*80)
        print("✅ TEST COMPLETE - ScraperAPI is working!")
        print("="*80 + "\n")
        
        # Check note.txt
        print("📝 Checking note.txt for errors...")
        try:
            with open('note.txt', 'r', encoding='utf-8', errors='ignore') as f:
                note_lines = f.readlines()[-50:]  # Last 50 lines
            
            scraperapi_mentions = [l for l in note_lines if 'scraperapi' in l.lower()]
            if scraperapi_mentions:
                print(f"   Found {len(scraperapi_mentions)} ScraperAPI log entries")
                for line in scraperapi_mentions[-5:]:
                    print(f"   {line.strip()}")
            else:
                print("   ⚠️  No ScraperAPI entries in note.txt yet")
        except FileNotFoundError:
            print("   ⚠️  note.txt not found")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*80)
        print("💡 TROUBLESHOOTING")
        print("="*80)
        print("""
1. Check if requests library is installed:
   pip install requests beautifulsoup4

2. Test ScraperAPI directly:
   import requests
   payload = {'api_key': '0afc0ab6e056e61161c0097ebbb5231a', 'url': 'https://httpbin.org/'}
   r = requests.get('https://api.scraperapi.com/', params=payload)
   print(r.status_code)  # Should be 200

3. Check ScraperAPI account at:
   https://dashboard.scraperapi.com/

4. Verify API key is active and has credits
        """)

if __name__ == "__main__":
    test_scraperapi_james_avery()
