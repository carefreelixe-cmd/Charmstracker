import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_all():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URL') or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'charmstracker')
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print(f"Connecting to database: {db_name}")
    print("Updating all charms to Active status...")
    print("="*60)
    
    # Get all charms
    charms = await db.charms.find({}).to_list(length=None)
    
    print(f"Found {len(charms)} charm(s)")
    print()
    
    for charm in charms:
        name = charm.get('name', 'Unknown')
        current_status = charm.get('status', 'MISSING')
        
        print(f"Charm: {name}")
        print(f"  Current status: {current_status}")
        
        # Update to Active
        await db.charms.update_one(
            {'_id': charm['_id']},
            {'$set': {
                'status': 'Active',
                'is_retired': False,
                'material': charm.get('material', 'Silver'),
                'popularity': charm.get('popularity', 50),
                'price_change_7d': charm.get('price_change_7d', 0.0),
                'price_change_30d': charm.get('price_change_30d', 0.0),
                'price_change_90d': charm.get('price_change_90d', 0.0)
            }}
        )
        print(f"  ✅ Updated to Active")
        print()
    
    print("="*60)
    print(f"✅ All {len(charms)} charm(s) now set to Active")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all())
