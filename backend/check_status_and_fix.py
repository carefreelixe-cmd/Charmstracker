"""
Check charm status in database and fix all to Active
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_and_fix():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URL') or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'charmtracker_production')
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("="*80)
    print("CHARM STATUS CHECK AND FIX")
    print("="*80)
    print(f"Database: {db_name}")
    print()
    
    # Get status counts
    total_charms = await db.charms.count_documents({})
    active_count = await db.charms.count_documents({'status': 'Active'})
    retired_count = await db.charms.count_documents({'status': 'Retired'})
    other_count = total_charms - active_count - retired_count
    
    print(f"📊 CURRENT STATUS DISTRIBUTION:")
    print(f"   Total charms: {total_charms}")
    print(f"   Active: {active_count}")
    print(f"   Retired: {retired_count}")
    print(f"   Other/Missing: {other_count}")
    print()
    
    if retired_count > 0 or other_count > 0:
        print(f"⚠️  Found {retired_count + other_count} charms that need fixing!")
        print()
        
        # Show some examples
        retired_charms = await db.charms.find({'status': 'Retired'}).limit(10).to_list(length=10)
        if retired_charms:
            print("📝 Examples of Retired charms:")
            for charm in retired_charms[:5]:
                print(f"   - {charm.get('name', 'Unknown')} (ID: {charm.get('id', 'N/A')})")
            if len(retired_charms) > 5:
                print(f"   ... and {len(retired_charms) - 5} more")
            print()
        
        # Ask for confirmation
        print("🔧 FIXING ALL CHARMS TO ACTIVE STATUS...")
        print()
        
        # Get list of charms that will be updated
        charms_to_fix = await db.charms.find(
            {'$or': [
                {'status': {'$ne': 'Active'}},
                {'is_retired': {'$ne': False}},
                {'status': {'$exists': False}},
                {'is_retired': {'$exists': False}}
            ]}
        ).to_list(length=None)
        
        if charms_to_fix:
            print(f"📝 Charms that will be fixed ({len(charms_to_fix)}):")
            for charm in charms_to_fix[:10]:
                old_status = charm.get('status', 'MISSING')
                old_retired = charm.get('is_retired', 'MISSING')
                print(f"   - {charm.get('name', 'Unknown')}: status={old_status}, is_retired={old_retired}")
            if len(charms_to_fix) > 10:
                print(f"   ... and {len(charms_to_fix) - 10} more")
            print()
        
        # Update all charms to Active
        result = await db.charms.update_many(
            {},  # Match all documents
            {'$set': {
                'status': 'Active',
                'is_retired': False
            }}
        )
        
        print(f"✅ Updated {result.modified_count} charms to Active status")
        print()
        
        # Verify the fix
        new_active_count = await db.charms.count_documents({'status': 'Active'})
        new_retired_count = await db.charms.count_documents({'status': 'Retired'})
        
        print("📊 FINAL STATUS DISTRIBUTION:")
        print(f"   Total charms: {total_charms}")
        print(f"   Active: {new_active_count}")
        print(f"   Retired: {new_retired_count}")
        print()
        
        if new_retired_count == 0 and new_active_count == total_charms:
            print("✅ SUCCESS! All charms are now Active!")
        else:
            print("⚠️  Some charms may still need attention")
    else:
        print("✅ All charms are already Active! No changes needed.")
    
    print()
    print("="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_and_fix())
