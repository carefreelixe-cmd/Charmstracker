"""
Script to fix missing or incorrect James Avery charm images
"""
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from scrapers.james_avery_scraper import JamesAveryScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

async def fix_charm_images():
    # Get MongoDB connection details
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "charmtracker_production")
    
    # Create MongoDB client with increased timeouts
    client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    db = client[db_name]
    
    scraper = JamesAveryScraper()
    
    async with scraper:
        try:
            # Test database connection
            await client.admin.command('ping')
            print("Successfully connected to MongoDB")
            
            # Get all charms that need image updates
            cursor = db.charms.find({
                "$or": [
                    {"images": {"$exists": False}},
                    {"images": {"$size": 0}},
                    {"images": None},
                    {"images": {"$elemMatch": {"$regex": "placeholder|placehold.co"}}},
                    {"james_avery_url": {"$exists": True, "$ne": None}}
                ]
            })
            charms = await cursor.to_list(length=None)
            
            print(f"Found {len(charms)} charms that need image updates")
            
            for charm in charms:
                try:
                        # First search for the charm on James Avery
                    search_results = await scraper.search_product(charm['name'])
                    
                    if search_results:
                        # Get product details from the first search result
                        product = await scraper.get_product_details(search_results[0])
                        
                        if product and product.get('images'):
                            # Update the charm with new images
                            await db.charms.update_one(
                                {"_id": charm["_id"]},
                                {"$set": {
                                    "images": product['images'],
                                    "james_avery_url": product.get('url')
                                }}
                            )
                            print(f"✅ Updated images for {charm['name']}")
                        else:
                            print(f"❌ No images found for {charm['name']}")
                    else:
                        print(f"❌ No James Avery product found for {charm['name']}")
                        
                    # Rate limiting
                    await asyncio.sleep(2)
                        # Update images list with all available images
                        images = []
                        if product['image_url']:
                            images.append(product['image_url'])
                        images.extend(product['additional_images'])
                        
                        # Update the charm's images
                        await db.charms.update_one(
                            {"id": charm['id']},
                            {"$set": {"images": images}}
                        )
                        print(f"Updated images for charm: {charm['name']}")
                    
                except Exception as e:
                    print(f"Error updating images for charm {charm['name']}: {str(e)}")
                    continue
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            raise
        
        finally:
            # Close the MongoDB client
            client.close()
            print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(fix_charm_images())