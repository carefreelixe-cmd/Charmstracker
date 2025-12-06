"""
Fix charm IDs to remove quotes and special characters
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

def clean_charm_name(name):
    """Clean charm name to create valid ID"""
    # Remove quotes
    cleaned = name.replace('"', '').replace("'", '')
    # Remove special characters
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)
    # Convert to lowercase and replace spaces/hyphens with underscore
    cleaned = cleaned.lower().replace(' ', '_').replace('-', '_')
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    return f"charm_{cleaned}"

async def fix_charm_ids():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URL') or os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'charmstracker')
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("Fixing charm IDs...")
    print("="*70)
    
    # Get all charms
    charms = await db.charms.find({}).to_list(length=None)
    
    fixed_count = 0
    
    for charm in charms:
        name = charm.get('name', '')
        current_id = charm.get('_id', '')
        
        # Generate clean ID
        clean_id = clean_charm_name(name)
        
        # Check if ID needs fixing (has quotes or special chars)
        if '%22' in str(current_id) or '"' in str(current_id) or clean_id != current_id:
            print(f"\nCharm: {name}")
            print(f"  Old ID: {current_id}")
            print(f"  New ID: {clean_id}")
            
            # Check if new ID already exists
            existing = await db.charms.find_one({'_id': clean_id})
            if existing and existing['_id'] != current_id:
                print(f"  ⚠️  SKIP: Clean ID already exists")
                continue
            
            # Update the document
            await db.charms.update_one(
                {'_id': charm['_id']},
                {'$set': {'_id': clean_id}}
            )
            
            # Also update the id field if it exists
            if 'id' in charm:
                await db.charms.update_one(
                    {'_id': clean_id},
                    {'$set': {'id': clean_id}}
                )
            
            print(f"  ✅ Fixed")
            fixed_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Fixed {fixed_count} charm ID(s)")
    print(f"{'='*70}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_charm_ids())
