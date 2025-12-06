"""
Mark all charms as Active
Since all charms are scraped from James Avery website, they should be Active
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_status():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_uri)
    db = client.charmstracker
    
    print("Adding status and is_retired fields to all charms...")
    print("="*50)
    
    # Update ALL charms to add status and is_retired fields
    result = await db.charms.update_many(
        {},  # Match all documents
        {"$set": {
            "status": "Active",
            "is_retired": False,
            "material": "Silver",  # Default material
            "popularity": 50,  # Default popularity
            "price_change_7d": 0.0,
            "price_change_30d": 0.0,
            "price_change_90d": 0.0
        }}
    )
    
    print(f"\n✅ Updated {result.modified_count} charm(s)")
    print(f"✅ All charms now have:")
    print(f"   - status: Active")
    print(f"   - is_retired: False")
    print(f"   - material: Silver")
    print("="*50)
    
    # Show updated charms
    charms = await db.charms.find({}).limit(5).to_list(length=5)
    print("\nSample charms:")
    for charm in charms:
        print(f"  {charm.get('name')}: status=\"{charm.get('status')}\" is_retired={charm.get('is_retired')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_status())
