"""
Test the AgentQL Etsy scraper directly
"""
import sys
sys.path.insert(0, '.')

from scrapers.agentql_scraper import AgentQLMarketplaceScraper

def test_etsy():
    """Test Etsy scraper with AgentQL"""
    
    print("="*60)
    print("Testing Etsy Scraper with AgentQL")
    print("="*60)
    
    # Create scraper (headless=False to see browser)
    scraper = AgentQLMarketplaceScraper(headless=False)
    
    # Test search
    charm_name = "james avery angel trumpet"
    print(f"\nSearching for: {charm_name}\n")
    
    # Run scrape
    listings = scraper.scrape_etsy(charm_name)
    
    # Display results
    print("\n" + "="*60)
    print(f"RESULTS: Found {len(listings)} Etsy listings")
    print("="*60)
    
    if listings:
        for i, listing in enumerate(listings[:5], 1):
            currency = listing.get('currency', 'USD')
            curr_symbol = {'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£'}.get(currency, '$')
            
            print(f"\n{i}. {listing.get('title', 'N/A')[:60]}")
            print(f"   Price: {curr_symbol}{listing.get('price', 0)} {currency}")
            print(f"   URL: {listing.get('url', 'N/A')[:70]}...")
    else:
        print("\n❌ No listings found!")
        print("This could mean:")
        print("1. AgentQL couldn't find the price elements")
        print("2. The page structure doesn't match our query")
        print("3. Etsy is blocking the scraper")
        print("\nCheck the browser window and etsy_agentql_debug.png screenshot")

if __name__ == "__main__":
    test_etsy()
