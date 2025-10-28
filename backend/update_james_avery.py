"""
Script to scrape and update James Avery charm data
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from scrapers.james_avery_scraper import JamesAveryScraper

async def update_james_avery_data():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection details
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "charmtracker_production")
    
    # Create MongoDB client
    client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    db = client[db_name]
    
    scraper = JamesAveryScraper()
    
    try:
        # Test database connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        async with scraper:
            # Get all charms from database
            cursor = db.charms.find({})
            charms = await cursor.to_list(length=None)
            print(f"Found {len(charms)} total charms to check")
            
            updated_count = 0
            for charm in charms:
                try:
                    # Get all charm URLs from browse pages
                    charm_urls = set()
                    category_urls = await scraper._get_category_urls()
                    
                    for category_url in category_urls:
                        product_urls = await scraper._get_product_urls_from_category(category_url)
                        charm_urls.update(product_urls)
                    
                    # Find matching charm by name
                    matched_product = None
                    for url in charm_urls:
                        product = await scraper._get_product_page(url)
                        if product and charm['name'].lower() in product['name'].lower():
                            matched_product = product
                            break
                    
                    if matched_product:
                        
                        # Update charm with James Avery data
                        update_data = {
                            "james_avery_url": matched_product["url"],
                            "james_avery_price": matched_product["price"],
                            "images": [matched_product["image_url"]] + matched_product["additional_images"]
                        }
                        
                        await db.charms.update_one(
                            {"id": charm["id"]},
                            {"$set": update_data}
                        )
                        
                        print(f"Updated charm: {charm['name']}")
                        updated_count += 1
                    
                except Exception as e:
                    print(f"Error updating charm {charm['name']}: {str(e)}")
                    continue
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(2)
            
            print(f"\nSuccessfully updated {updated_count} charms")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        client.close()
        print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(update_james_avery_data())