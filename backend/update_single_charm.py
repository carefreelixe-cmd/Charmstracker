"""
Script to update a single charm's images from James Avery
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from scrapers.james_avery_scraper import JamesAveryScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_single_charm(charm_name: str):
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection details
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "charmtracker_production")
    
    # Create MongoDB client
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Initialize scraper
    scraper = JamesAveryScraper()
    
    try:
        # Test database connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get charm from James Avery website
        logger.info(f"Searching for: {charm_name}")
        category_url = f"{scraper.base_url}/charms"
        product_urls = await scraper._get_product_urls_from_category(category_url)
        
        if product_urls:
            # Find the most relevant product URL
            matching_url = next((url for url in product_urls if charm_name.lower() in url.lower()), None)
            if matching_url:
                # Get product details
                product = await scraper._get_product_page(matching_url)
            
            if product and product.get('images'):
                # Update charm in database
                result = await db.charms.update_one(
                    {"name": {"$regex": f"^{charm_name}$", "$options": "i"}},
                    {
                        "$set": {
                            "images": product['images'],
                            "james_avery_url": product.get('url'),
                            "james_avery_price": product.get('price')
                        }
                    }
                )
                if result.modified_count > 0:
                    logger.info(f"✅ Updated {charm_name} with {len(product['images'])} images")
                else:
                    logger.warning(f"⚠️ No charm found to update: {charm_name}")
            else:
                logger.error(f"❌ No images found for: {charm_name}")
        else:
            logger.error(f"❌ No search results for: {charm_name}")
            
    except Exception as e:
        logger.error(f"Error updating charm: {str(e)}")
    finally:
        client.close()
        logger.info("Connections closed")

if __name__ == "__main__":
    # Test with Cross Charm
    asyncio.run(update_single_charm("Cross Charm"))