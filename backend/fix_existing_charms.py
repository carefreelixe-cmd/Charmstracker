"""
Quick fix to add missing fields to existing charms in database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL', "mongodb://localhost:27017/")
DB_NAME = os.getenv('DB_NAME', "charmstracker")

async def fix_charms():
    print("Fixing existing charms in database...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Add missing fields to all charms
    result = await db.charms.update_many(
        {},
        {'$set': {
            'price_change_7d': 0.0,
            'price_change_30d': 0.0,
            'price_change_90d': 0.0,
            'popularity': 75
        }}
    )
    
    print(f"✅ Updated {result.modified_count} charms with missing fields")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_charms())
