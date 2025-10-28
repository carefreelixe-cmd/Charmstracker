"""
Enhanced seed script to fetch all James Avery charms
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from scrapers.james_avery_scraper import JamesAveryScraper
from models.db_setup import setup_mongodb_indexes
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.scraper')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_all_charms():
    """Fetch and store all charms from James Avery"""
    client = None
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        db_name = os.getenv('DB_NAME', 'charmstracker')
        
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        # Setup database indexes
        setup_mongodb_indexes(db)
        
        # Initialize scraper
        async with JamesAveryScraper() as scraper:
            # Fetch all charms
            logger.info("Starting to fetch all James Avery charms...")
            charms = await scraper.get_all_charms()
            
            logger.info(f"Found {len(charms)} charms")
        
        # Process each charm
        for charm in charms:
            try:
                # Normalize the data
                charm_data = {
                    'name': charm['name'],
                    'description': charm.get('description', ''),
                    'material': 'Sterling Silver',  # Default, will be updated if gold version exists
                    'status': charm['status'],
                    'is_retired': charm['is_retired'],
                    'james_avery_price': charm.get('price'),
                    'james_avery_url': charm['url'],
                    'avg_price': charm.get('price', 0.0),  # Will be updated with market data
                    'price_history': [{
                        'date': datetime.utcnow(),
                        'price': charm.get('price', 0.0),
                        'source': 'james_avery'
                    }] if charm.get('price') else [],
                    'images': [charm['image_url']] + charm.get('additional_images', []) if charm.get('image_url') else [],
                    'last_updated': datetime.utcnow(),
                    'created_at': datetime.utcnow()
                }
                
                # Check if charm already exists
                existing = await db.charms.find_one({'name': charm['name']})
                
                if existing:
                    # Update existing charm
                    await db.charms.update_one(
                        {'_id': existing['_id']},
                        {
                            '$set': {
                                'description': charm_data['description'],
                                'status': charm_data['status'],
                                'is_retired': charm_data['is_retired'],
                                'james_avery_price': charm_data['james_avery_price'],
                                'james_avery_url': charm_data['james_avery_url'],
                                'last_updated': datetime.utcnow()
                            },
                            '$addToSet': {
                                'images': {
                                    '$each': charm_data['images']
                                }
                            }
                        }
                    )
                    logger.info(f"Updated charm: {charm['name']}")
                else:
                    # Insert new charm
                    await db.charms.insert_one(charm_data)
                    logger.info(f"Added new charm: {charm['name']}")
                
            except Exception as e:
                logger.error(f"Error processing charm {charm['name']}: {str(e)}")
                continue
        
        logger.info("Completed charm database update")
        
    except Exception as e:
        logger.error(f"Error in seed script: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_all_charms())