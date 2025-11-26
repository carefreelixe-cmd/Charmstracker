"""
Test AgentQL scraper specifically for James Avery "Jesus Loves Me Charm"
This will show exactly what AgentQL is finding and why charm details aren't showing
"""
from scrapers.agentql_scraper import AgentQLMarketplaceScraper
import json

def test_james_avery_charm():
    """Test AgentQL with Jesus Loves Me Charm"""
    
    charm_name = "James Avery Jesus Loves Me Charm"
    
    print("\n" + "="*80)
    print(f"🧪 TESTING AGENTQL FOR: {charm_name}")
    print("="*80 + "\n")
    
    print("⚙️  Configuration:")
    print("   - headless=False (you'll see the browser)")
    print("   - Will scrape: Etsy, eBay, Poshmark")
    print("   - Using AgentQL AI to extract data")
    print("\n" + "-"*80 + "\n")
    
    try:
        # Create scraper with visible browser so you can see what's happening
        scraper = AgentQLMarketplaceScraper(headless=False)
        
        print("\n🎯 Starting scraping process...\n")
        
        # Scrape all marketplaces
        results = scraper.scrape_all(charm_name)
        
        # Print summary
        print("\n" + "="*80)
        print("📊 RESULTS SUMMARY")
        print("="*80 + "\n")
        
        if not results:
            print("❌ NO RESULTS FOUND!")
            print("\nPossible reasons:")
            print("  1. Bot detection blocked the scrapers")
            print("  2. AgentQL couldn't find the product elements")
            print("  3. Search query didn't match any listings")
            print("  4. AGENTQL_API_KEY not configured or invalid")
            return
        
        # Group by platform
        by_platform = {}
        for listing in results:
            platform = listing.get('platform', 'Unknown')
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(listing)
        
        # Print detailed results
        for platform, listings in by_platform.items():
            print(f"\n{'='*60}")
            print(f"🏪 {platform.upper()} - {len(listings)} listings")
            print(f"{'='*60}")
            
            for i, listing in enumerate(listings, 1):
                print(f"\n  {i}. {listing.get('title', 'No title')}")
                print(f"     💰 Price: ${listing.get('price', 0)}")
                print(f"     🔗 URL: {listing.get('url', 'No URL')[:80]}")
                print(f"     🖼️  Image: {listing.get('image_url', 'No image')[:80]}")
                print(f"     📦 Condition: {listing.get('condition', 'Unknown')}")
        
        # Calculate average price
        prices = [l['price'] for l in results if l.get('price', 0) > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"\n{'='*60}")
            print(f"💵 AVERAGE PRICE: ${avg_price:.2f}")
            print(f"   Min: ${min(prices):.2f}")
            print(f"   Max: ${max(prices):.2f}")
            print(f"{'='*60}")
        
        # Save to file
        output_file = 'test_agentql_james_avery_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        # Check note.txt errors
        print("\n" + "="*80)
        print("🔍 ANALYZING ERRORS FROM note.txt")
        print("="*80)
        
        try:
            with open('note.txt', 'r', encoding='utf-8') as f:
                note_content = f.read()
            
            # Look for AgentQL errors
            if 'AgentQL' in note_content:
                print("\n✅ AgentQL activity found in note.txt")
                
                # Count error types
                error_keywords = {
                    'Bot detection': ['bot detection', 'captcha', 'challenge'],
                    'No products found': ['no products found', 'no items found', 'no listings found'],
                    'AgentQL error': ['agentql error', 'playwright error'],
                    'API key': ['api_key', 'agentql_api_key']
                }
                
                for error_type, keywords in error_keywords.items():
                    count = sum(note_content.lower().count(kw) for kw in keywords)
                    if count > 0:
                        print(f"  ⚠️  {error_type}: {count} occurrences")
            else:
                print("\n❌ No AgentQL activity in note.txt")
                print("   This means AgentQL scraper might not be running at all")
        
        except FileNotFoundError:
            print("\n⚠️  note.txt not found")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*80)
        print("💡 TROUBLESHOOTING TIPS")
        print("="*80)
        print("""
1. Check if AGENTQL_API_KEY is set in .env file:
   - Open backend/.env
   - Look for: AGENTQL_API_KEY=your_key_here

2. Check if agentql and playwright are installed:
   pip install agentql playwright
   playwright install chromium

3. Check if the charm exists in the database:
   - Open MongoDB
   - Check 'charms' collection
   - Look for "Jesus Loves Me Charm"

4. Check note.txt for detailed error logs
        """)

if __name__ == "__main__":
    test_james_avery_charm()
