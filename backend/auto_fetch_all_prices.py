"""
Auto-fetch live prices for all charms
Runs scraper for each charm and updates database
Prevents duplicate listings by checking scraped_at date
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraperapi_client import ScraperAPIClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def auto_fetch_all_charms():
    """Fetch live prices for all charms automatically"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URL') or os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'charmstracker')
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("="*70)
    print("AUTO-FETCHING LIVE PRICES FOR ALL CHARMS")
    print("="*70)
    
    # Get all charms
    charms = await db.charms.find({}).to_list(length=None)
    total_charms = len(charms)
    
    print(f"\nFound {total_charms} charms")
    print(f"Starting scraping process...\n")
    
    scraper = ScraperAPIClient()
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, charm in enumerate(charms, 1):
        charm_name = charm.get('name', 'Unknown')
        charm_id = charm.get('_id', '')
        last_updated = charm.get('last_updated')
        
        print(f"\n[{idx}/{total_charms}] {charm_name}")
        print(f"  ID: {charm_id}")
        
        # Check if already updated today (skip if less than 6 hours old)
        if last_updated:
            if isinstance(last_updated, str):
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            
            hours_since_update = (datetime.utcnow() - last_updated).total_seconds() / 3600
            
            if hours_since_update < 6:
                print(f"  ⏭️  SKIP: Updated {hours_since_update:.1f}h ago (< 6h)")
                skipped_count += 1
                continue
        
        try:
            # Scrape live prices
            print(f"  🔍 Fetching live prices...")
            all_listings = scraper.scrape_all(f"James Avery {charm_name}")
            
            if not all_listings:
                print(f"  ⚠️  No listings found")
                error_count += 1
                continue
            
            # Remove duplicates based on URL and title
            unique_listings = {}
            for listing in all_listings:
                # Create unique key (url + title for non-eBay, title + price for eBay without URL)
                if listing.get('url'):
                    key = f"{listing['url']}"
                else:
                    key = f"{listing['platform']}_{listing['title']}_{listing['price']}"
                
                # Keep first occurrence (usually best match)
                if key not in unique_listings:
                    unique_listings[key] = listing
            
            deduplicated_listings = list(unique_listings.values())
            
            print(f"  ✅ Found {len(all_listings)} listings ({len(deduplicated_listings)} unique)")
            
            # Calculate average price
            if deduplicated_listings:
                prices = [l['price'] for l in deduplicated_listings if l.get('price', 0) > 0]
                avg_price = sum(prices) / len(prices) if prices else 0
            else:
                avg_price = 0
            
            # Format listings for database
            formatted_listings = []
            for listing in deduplicated_listings[:50]:  # Keep max 50 listings
                formatted_listings.append({
                    'platform': listing['platform'].lower(),
                    'marketplace': listing['platform'],
                    'title': listing.get('title', ''),
                    'price': listing.get('price', 0),
                    'url': listing.get('url', ''),
                    'condition': listing.get('condition', 'Used'),
                    'image_url': listing.get('image_url', ''),
                    'seller': listing.get('seller', ''),
                    'scraped_at': datetime.utcnow()
                })
            
            # Update charm in database
            await db.charms.update_one(
                {'_id': charm_id},
                {
                    '$set': {
                        'listings': formatted_listings,
                        'average_price': round(avg_price, 2),
                        'listing_count': len(formatted_listings),
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            print(f"  💾 Updated database: {len(formatted_listings)} listings, avg ${avg_price:.2f}")
            updated_count += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
            continue
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print(f"✅ Updated: {updated_count} charms")
    print(f"⏭️  Skipped: {skipped_count} charms (recently updated)")
    print(f"❌ Errors: {error_count} charms")
    print(f"📊 Total: {total_charms} charms")
    print("="*70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(auto_fetch_all_charms())
