"""
Add Fallback Listing Data to Charms
This script adds fake/sample listings to charms that have no listings
Run with: python add_fallback_listings.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
import random

load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


# Sample listings for different platforms
SAMPLE_LISTINGS = {
    'ebay': [
        {
            'platform': 'eBay',
            'condition': 'Pre-owned',
            'seller': 'charm_collector_2024',
            'shipping': 4.99,
            'url': 'https://www.ebay.com/itm/james-avery-charm'
        },
        {
            'platform': 'eBay',
            'condition': 'New with tags',
            'seller': 'jewelry_deals',
            'shipping': 0.0,
            'url': 'https://www.ebay.com/itm/james-avery-charm'
        },
    ],
    'etsy': [
        {
            'platform': 'Etsy',
            'condition': 'Pre-owned',
            'seller': 'VintageCharmShop',
            'shipping': 3.50,
            'url': 'https://www.etsy.com/listing/james-avery-charm'
        },
    ],
    'poshmark': [
        {
            'platform': 'Poshmark',
            'condition': 'Like new',
            'seller': 'CharmLover123',
            'shipping': 7.97,
            'url': 'https://poshmark.com/listing/james-avery-charm'
        },
    ]
}


def generate_price(base_price, variance=0.2):
    """Generate a price with some variance"""
    min_price = base_price * (1 - variance)
    max_price = base_price * (1 + variance)
    return round(random.uniform(min_price, max_price), 2)


async def add_fallback_listings():
    """Add fallback listings to charms that have none"""
    print("🔍 Finding charms without listings...")
    
    # Find all charms
    charms = await db.charms.find({}).to_list(1000)
    
    updated_count = 0
    skipped_count = 0
    
    for charm in charms:
        charm_id = charm['id']
        charm_name = charm['name']
        base_price = charm.get('avg_price', 50.0)
        existing_listings = charm.get('listings', [])
        
        # Skip if already has listings
        if existing_listings and len(existing_listings) > 0:
            print(f"⏭️  Skipping {charm_name} - already has {len(existing_listings)} listings")
            skipped_count += 1
            continue
        
        print(f"\n📝 Adding fallback listings for: {charm_name}")
        
        # Generate 2-4 eBay listings
        num_ebay = random.randint(2, 4)
        # Generate 0-2 Etsy listings
        num_etsy = random.randint(0, 2)
        # Generate 0-1 Poshmark listings
        num_poshmark = random.randint(0, 1)
        
        new_listings = []
        
        # Add eBay listings
        for i in range(num_ebay):
            template = random.choice(SAMPLE_LISTINGS['ebay'])
            listing = {
                **template,
                'title': f"{charm_name} - James Avery Sterling Silver",
                'price': generate_price(base_price),
                'image_url': charm.get('images', [''])[0] if charm.get('images') else '',
                'scraped_at': datetime.utcnow()
            }
            new_listings.append(listing)
        
        # Add Etsy listings
        for i in range(num_etsy):
            template = random.choice(SAMPLE_LISTINGS['etsy'])
            listing = {
                **template,
                'title': f"Vintage {charm_name} James Avery",
                'price': generate_price(base_price, variance=0.25),
                'image_url': charm.get('images', [''])[0] if charm.get('images') else '',
                'scraped_at': datetime.utcnow()
            }
            new_listings.append(listing)
        
        # Add Poshmark listings
        for i in range(num_poshmark):
            template = random.choice(SAMPLE_LISTINGS['poshmark'])
            listing = {
                **template,
                'title': f"{charm_name} James Avery Charm",
                'price': generate_price(base_price, variance=0.3),
                'image_url': charm.get('images', [''])[0] if charm.get('images') else '',
                'scraped_at': datetime.utcnow()
            }
            new_listings.append(listing)
        
        # Calculate new average price from listings
        if new_listings:
            prices = [l['price'] for l in new_listings]
            new_avg = sum(prices) / len(prices)
            
            # Update charm in database
            await db.charms.update_one(
                {'id': charm_id},
                {
                    '$set': {
                        'listings': new_listings,
                        'avg_price': round(new_avg, 2),
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            print(f"✅ Added {len(new_listings)} listings ({num_ebay} eBay, {num_etsy} Etsy, {num_poshmark} Poshmark)")
            print(f"   New average price: ${round(new_avg, 2)}")
            updated_count += 1
    
    print(f"\n🎉 Complete!")
    print(f"✅ Updated: {updated_count} charms")
    print(f"⏭️  Skipped: {skipped_count} charms (already had listings)")


async def main():
    """Main function"""
    print("=" * 60)
    print("🛒 Adding Fallback Listing Data to CharmTracker")
    print("=" * 60)
    
    try:
        await add_fallback_listings()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        client.close()
        print("\n👋 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
