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
    
    print("Marking all charms as Active...")
    print("="*50)
    
    # Get all charms
    charms = await db.charms.find({}).to_list(length=None)
    
    fixed_count = 0
    
    for charm in charms:
        status = charm.get('status', '')
        charm_id = charm.get('id', 'unknown')
        charm_name = charm.get('name', 'unknown')
        
        print(f"\nCharm: {charm_name}")
        print(f"  Current status: '{status}'")
        
        # Mark all as Active
        if status != "Active":
            print(f"  🔄 Updating to Active")
            
            # Update the charm to Active and set is_retired to False
            await db.charms.update_one(
                {"id": charm_id},
                {"$set": {"status": "Active", "is_retired": False}}
            )
            fixed_count += 1
        else:
            print(f"  ✅ Already Active")
    
    print(f"\n{'='*50}")
    print(f"✅ Updated {fixed_count} charm(s) to Active")
    print(f"✅ Total charms: {len(charms)}")
    print(f"{'='*50}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_status())
