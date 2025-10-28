"""
Script to check database status
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_database():
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
        
        # Count total charms
        total_charms = await db.charms.count_documents({})
        print(f"Total charms in database: {total_charms}")
        
        # Count James Avery charms
        ja_charms = await db.charms.count_documents({"james_avery_url": {"$exists": True, "$ne": None}})
        print(f"James Avery charms: {ja_charms}")
        
        # Get sample charm
        if total_charms > 0:
            sample = await db.charms.find_one({})
            print("\nSample charm:")
            print(f"Name: {sample.get('name')}")
            print(f"Material: {sample.get('material')}")
            print(f"Images: {sample.get('images', [])}")
            print(f"James Avery URL: {sample.get('james_avery_url')}")
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise
    finally:
        client.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    asyncio.run(check_database())