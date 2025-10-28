"""
Script to update charm images from placeholders to real images
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Define a mapping of charm names to their actual image URLs
CHARM_IMAGES = {
    "Cross Charm": [
        "https://www.jamesavery.com/images/charms/cross-charm-silver-1.jpg",
        "https://www.jamesavery.com/images/charms/cross-charm-silver-2.jpg"
    ],
    "Heart Charm": [
        "https://www.jamesavery.com/images/charms/heart-charm-silver-1.jpg",
        "https://www.jamesavery.com/images/charms/heart-charm-silver-2.jpg"
    ],
    # Add more mappings as needed
}

async def update_charm_images():
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
    
    try:
        # Test database connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Update charms with placeholder images
        cursor = db.charms.find({"images": {"$regex": "placehold.co"}})
        charms = await cursor.to_list(length=None)
        
        print(f"Found {len(charms)} charms with placeholder images")
        
        updated_count = 0
        for charm in charms:
            name = charm['name']
            
            # For charms without specific mappings, use generic jewelry images
            new_images = CHARM_IMAGES.get(name, [
                f"https://source.unsplash.com/featured/?silver,charm,{name.replace(' ', '').lower()}",
                f"https://source.unsplash.com/featured/?jewelry,charm,{name.replace(' ', '').lower()}"
            ])
            
            # Update the charm's images
            await db.charms.update_one(
                {"id": charm["id"]},
                {"$set": {"images": new_images}}
            )
            
            print(f"Updated images for: {name}")
            updated_count += 1
            
        print(f"\nSuccessfully updated {updated_count} charms")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        client.close()
        print("Database connection closed")

if __name__ == "__main__":
    asyncio.run(update_charm_images())