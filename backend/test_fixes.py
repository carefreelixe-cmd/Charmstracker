"""
Test script to verify all fixes are working
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_all():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URL') or os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'charmstracker')
    
    if not mongo_uri:
        print("❌ MONGO_URL not found in .env")
        return
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("="*70)
    print(f"CHECKING DATABASE: {db_name}")
    print("="*70)
    
    # Check 1: How many charms exist
    total_charms = await db.charms.count_documents({})
    print(f"\n1. Total Charms: {total_charms}")
    
    if total_charms == 0:
        print("   ❌ NO CHARMS IN DATABASE!")
        client.close()
        return
    
    # Check 2: Status field distribution
    active_count = await db.charms.count_documents({"status": "Active"})
    retired_count = await db.charms.count_documents({"status": "Retired"})
    no_status = await db.charms.count_documents({"status": {"$exists": False}})
    
    print(f"\n2. Status Distribution:")
    print(f"   ✅ Active: {active_count}")
    print(f"   ⚠️  Retired: {retired_count}")
    print(f"   ❌ No Status: {no_status}")
    
    if active_count == 0:
        print("   ❌ PROBLEM: No charms marked as Active!")
    
    # Check 3: Sample charms
    print(f"\n3. Sample Charms (first 5):")
    charms = await db.charms.find({}).limit(5).to_list(length=5)
    for charm in charms:
        name = charm.get('name', 'Unknown')
        status = charm.get('status', 'MISSING')
        is_retired = charm.get('is_retired', 'MISSING')
        listings_count = len(charm.get('listings', []))
        
        print(f"   • {name}")
        print(f"     Status: {status} | is_retired: {is_retired} | Listings: {listings_count}")
    
    # Check 4: Charms with listings
    charms_with_listings = await db.charms.count_documents({"listings.0": {"$exists": True}})
    print(f"\n4. Charms with Listings: {charms_with_listings}/{total_charms}")
    
    if charms_with_listings > 0:
        sample = await db.charms.find_one({"listings.0": {"$exists": True}})
        if sample:
            print(f"   Sample charm with listings: {sample.get('name')}")
            print(f"   Number of listings: {len(sample.get('listings', []))}")
            
            # Check if listings have URLs
            listings = sample.get('listings', [])
            has_url = sum(1 for l in listings if l.get('url'))
            no_url = len(listings) - has_url
            
            print(f"   Listings with URLs: {has_url}")
            print(f"   Listings without URLs: {no_url}")
            
            if has_url > 0:
                print("   ✅ Listings have purchase links")
            else:
                print("   ⚠️  No purchase links in listings")
    
    # Check 5: Required fields
    print(f"\n5. Checking Required Fields:")
    missing_material = await db.charms.count_documents({"material": {"$exists": False}})
    missing_popularity = await db.charms.count_documents({"popularity": {"$exists": False}})
    missing_price_change = await db.charms.count_documents({"price_change_7d": {"$exists": False}})
    
    print(f"   Missing material: {missing_material}")
    print(f"   Missing popularity: {missing_popularity}")
    print(f"   Missing price_change_7d: {missing_price_change}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    issues = []
    
    if total_charms == 0:
        issues.append("❌ No charms in database")
    
    if active_count == 0:
        issues.append("❌ All charms marked as Retired (should be Active)")
    
    if charms_with_listings == 0:
        issues.append("⚠️  No charms have marketplace listings")
    
    if missing_material > 0 or missing_popularity > 0 or missing_price_change > 0:
        issues.append("⚠️  Some charms missing required fields")
    
    if len(issues) == 0:
        print("✅ ALL CHECKS PASSED!")
        print("✅ Database is properly configured")
        print("✅ Charms have Active status")
        print("✅ Listings are available")
    else:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n📝 RECOMMENDED ACTIONS:")
        if active_count == 0:
            print("  1. Run: python make_all_active.py")
        if charms_with_listings == 0:
            print("  2. Scrape data for charms (use Fetch Live Prices)")
    
    print("="*70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_all())
