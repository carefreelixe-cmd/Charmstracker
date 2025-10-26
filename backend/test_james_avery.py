import asyncio
import logging
from scrapers.james_avery_scraper import james_avery_scraper
from motor.motor_asyncio import AsyncIOMotorClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_scraper():
    print("=" * 70)
    print("TESTING JAMES AVERY SCRAPER")
    print("=" * 70)
    
    # Test with a few charm names
    test_charms = [
        "Heart Charm",
        "Cross Charm",
        "Angel Charm"
    ]
    
    for charm_name in test_charms:
        print(f"\n{'='*70}")
        print(f"Testing: {charm_name}")
        print(f"{'='*70}")
        
        try:
            # Scrape data
            result = await james_avery_scraper.get_charm_details(charm_name)
            
            if result:
                print(f"✅ SUCCESS - Found data for {charm_name}")
                print(f"\nName: {result.get('name')}")
                print(f"Description: {result.get('description', '')[:100]}...")
                print(f"Material: {result.get('material')}")
                print(f"Status: {result.get('status')}")
                print(f"Is Retired: {result.get('is_retired')}")
                print(f"Price: ${result.get('official_price', 'N/A')}")
                print(f"URL: {result.get('official_url')}")
                
                images = result.get('images', [])
                print(f"\n📷 Images ({len(images)}):")
                for idx, img in enumerate(images, 1):
                    print(f"  {idx}. {img}")
                    # Check if it's a bad image
                    if 'flyout' in img.lower() or 'navigation' in img.lower():
                        print(f"     ⚠️ WARNING: This is a navigation/flyout image!")
                
                # Now check what would be saved to DB
                print(f"\n💾 Data that would be saved to DB:")
                print(f"  - Name: {result.get('name')}")
                print(f"  - Images: {len(images)} images")
                print(f"  - Material: {result.get('material')}")
                print(f"  - Status: {result.get('status')}")
                
            else:
                print(f"❌ FAILED - No data found for {charm_name}")
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print()
        await asyncio.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 70)
    print("Now checking what's actually in the database...")
    print("=" * 70)
    
    # Connect to DB and check a few charms
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.charmtracker
    
    charms = await db.charms.find().limit(5).to_list(length=5)
    
    for charm in charms:
        name = charm.get('name', 'Unknown')
        images = charm.get('images', [])
        print(f"\n🔍 {name}")
        print(f"   Images in DB: {len(images)}")
        if images:
            for idx, img in enumerate(images, 1):
                print(f"   {idx}. {img[:80]}{'...' if len(img) > 80 else ''}")
                if 'flyout' in img.lower():
                    print(f"      ⚠️ BAD IMAGE - Contains 'flyout'")
        else:
            print(f"   ⚠️ NO IMAGES!")
    
    await client.close()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_scraper())
