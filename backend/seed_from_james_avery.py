"""
Seed/Update Charms from James Avery Website
Scrapes real data (images, prices, descriptions) from James Avery
Prevents duplicates by updating existing charms
Run with: python seed_from_james_avery.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from scrapers.james_avery_scraper import JamesAveryScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


def generate_charm_id(name: str) -> str:
    """Generate consistent charm ID from name"""
    import re
    # Remove special characters and convert to lowercase
    clean_name = re.sub(r'[^a-z0-9\s]', '', name.lower())
    # Replace spaces with underscores
    charm_id = f"charm_{clean_name.replace(' ', '_')}"
    return charm_id


async def seed_charms_from_james_avery():
    """Seed/update charms from James Avery website"""
    print("=" * 60)
    print("🌱 Seeding Charms from James Avery Website")
    print("=" * 60)
    
    async with JamesAveryScraper() as scraper:
        # Get all charm URLs from James Avery (faster)
        print("\n🔍 Finding charm URLs from James Avery...")
        print("⏳ This may take several minutes...")
        
        all_charms = await scraper.get_all_charms()
        
        if not all_charms:
            print("❌ No charms found!")
            return
        
        print(f"\n✅ Found {len(all_charms)} charms from James Avery")
        print("\n📊 Processing and saving ONE BY ONE to database...")
        print("💡 If script crashes, already saved charms will remain in database!")
        
        new_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, charm_data in enumerate(all_charms, 1):
            try:
                name = charm_data.get('name', '')
                if not name:
                    logger.warning(f"Skipping charm without name: {charm_data}")
                    skipped_count += 1
                    continue
                
                # Generate consistent ID
                charm_id = generate_charm_id(name)
                
                # Check if charm already exists
                existing_charm = await db.charms.find_one({'id': charm_id})
                
                # Prepare charm document
                charm_doc = {
                    'id': charm_id,
                    'name': name,
                    'description': charm_data.get('description', f"{name} from James Avery."),
                    'material': charm_data.get('material', 'Silver'),
                    'status': charm_data.get('status', 'Active'),
                    'is_retired': charm_data.get('is_retired', False),
                    'james_avery_price': charm_data.get('official_price'),
                    'james_avery_url': charm_data.get('official_url'),
                    'avg_price': charm_data.get('official_price', 50.0),
                    'price_change_7d': 0.0,
                    'price_change_30d': 0.0,
                    'price_change_90d': 0.0,
                    'popularity': 50,
                    'images': charm_data.get('images', []),
                    'listings': [],
                    'price_history': [],
                    'related_charm_ids': [],
                    'last_updated': datetime.utcnow(),
                }
                
                if existing_charm:
                    # Update existing charm
                    # Keep price history and listings if they exist
                    charm_doc['price_history'] = existing_charm.get('price_history', [])
                    charm_doc['listings'] = existing_charm.get('listings', [])
                    charm_doc['related_charm_ids'] = existing_charm.get('related_charm_ids', [])
                    charm_doc['created_at'] = existing_charm.get('created_at', datetime.utcnow())
                    
                    # Only update if images or price changed
                    needs_update = False
                    if charm_doc['images'] != existing_charm.get('images', []):
                        logger.info(f"   📷 Images updated for {name}")
                        needs_update = True
                    if charm_doc['james_avery_price'] != existing_charm.get('james_avery_price'):
                        logger.info(f"   💰 Price updated for {name}: ${existing_charm.get('james_avery_price', 0)} → ${charm_doc['james_avery_price']}")
                        needs_update = True
                    
                    if needs_update:
                        # 💾 SAVE TO DATABASE IMMEDIATELY
                        await db.charms.update_one(
                            {'id': charm_id},
                            {'$set': charm_doc}
                        )
                        updated_count += 1
                        print(f"✏️  [{idx}/{len(all_charms)}] Updated & SAVED: {name}")
                    else:
                        skipped_count += 1
                        print(f"⏭️  [{idx}/{len(all_charms)}] Skipped: {name} (no changes)")
                else:
                    # Insert new charm
                    charm_doc['created_at'] = datetime.utcnow()
                    
                    # 💾 SAVE TO DATABASE IMMEDIATELY
                    await db.charms.insert_one(charm_doc)
                    new_count += 1
                    print(f"✅ [{idx}/{len(all_charms)}] Added & SAVED: {name}")
                    if charm_doc['images']:
                        print(f"   📷 {len(charm_doc['images'])} images")
                    if charm_doc['james_avery_price']:
                        print(f"   💰 ${charm_doc['james_avery_price']}")
                
                # Flush to ensure data is saved
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing charm {idx}: {str(e)}")
                error_count += 1
                continue
        
        print("\n" + "=" * 60)
        print("🎉 Seeding Complete!")
        print("=" * 60)
        print(f"✅ New charms added: {new_count}")
        print(f"✏️  Charms updated: {updated_count}")
        print(f"⏭️  Charms skipped: {skipped_count}")
        if error_count > 0:
            print(f"❌ Errors: {error_count}")
        print(f"📊 Total processed: {len(all_charms)}")


async def update_single_charm(charm_name: str):
    """Update a single charm from James Avery"""
    print(f"\n🔄 Updating charm: {charm_name}")
    
    async with JamesAveryScraper() as scraper:
        # Get charm details
        charm_data = await scraper.get_charm_details(charm_name)
        
        if not charm_data:
            print(f"❌ Charm not found: {charm_name}")
            return
        
        name = charm_data.get('name', charm_name)
        charm_id = generate_charm_id(name)
        
        # Check if exists
        existing_charm = await db.charms.find_one({'id': charm_id})
        
        if not existing_charm:
            print(f"❌ Charm not in database: {charm_id}")
            return
        
        # Update charm
        update_doc = {
            'name': name,
            'description': charm_data.get('description', existing_charm.get('description')),
            'material': charm_data.get('material', existing_charm.get('material')),
            'status': charm_data.get('status', existing_charm.get('status')),
            'is_retired': charm_data.get('is_retired', existing_charm.get('is_retired')),
            'james_avery_price': charm_data.get('official_price', existing_charm.get('james_avery_price')),
            'james_avery_url': charm_data.get('official_url', existing_charm.get('james_avery_url')),
            'images': charm_data.get('images', existing_charm.get('images', [])),
            'last_updated': datetime.utcnow(),
        }
        
        await db.charms.update_one(
            {'id': charm_id},
            {'$set': update_doc}
        )
        
        print(f"✅ Updated: {name}")
        print(f"   📷 Images: {len(update_doc['images'])}")
        print(f"   💰 Price: ${update_doc['james_avery_price']}")
        print(f"   🔗 URL: {update_doc['james_avery_url']}")


async def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        # Update single charm
        charm_name = ' '.join(sys.argv[1:])
        await update_single_charm(charm_name)
    else:
        # Seed all charms
        await seed_charms_from_james_avery()
    
    client.close()
    print("\n👋 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
