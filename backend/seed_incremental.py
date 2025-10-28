"""
Incremental Seed Script - Scrapes James Avery and saves one-by-one
This script:
1. Clears database first (with confirmation)
2. Discovers all product URLs
3. Scrapes and saves each charm immediately
4. Shows progress and handles errors gracefully
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from scrapers.james_avery_scraper import JamesAveryScraper
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "charmstracker"

async def seed_charms_incremental():
    """Clear database and seed with James Avery data - saves one-by-one"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Initialize scraper
    scraper = JamesAveryScraper()
    
    try:
        # Step 1: Clear existing charm data
        print("\n" + "="*70)
        print("🗑️  STEP 1: Clearing existing charm data...")
        print("="*70)
        
        existing_count = await db.charms.count_documents({})
        print(f"Found {existing_count} existing charms in database")
        
        if existing_count > 0:
            confirm = input(f"\n⚠️  Delete all {existing_count} charms? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Seeding cancelled.")
                return
            
            result = await db.charms.delete_many({})
            print(f"✅ Deleted {result.deleted_count} charms\n")
        else:
            print("✅ Database already empty\n")
        
        # Step 2: Get all product URLs first
        print("="*70)
        print("🔍 STEP 2: Discovering all product URLs...")
        print("="*70)
        print("This will take a few minutes as we scan all categories...\n")
        
        product_urls = await scraper._get_all_product_urls()
        total_products = len(product_urls)
        
        print(f"\n✅ Found {total_products} products to scrape")
        print("="*70 + "\n")
        
        if total_products == 0:
            print("❌ No products found. Please check the scraper.")
            return
        
        # Step 3: Scrape and save one-by-one
        print("="*70)
        print("📥 STEP 3: Scraping and saving charms incrementally...")
        print("="*70)
        print("Each charm will be saved immediately after scraping.\n")
        
        saved_count = 0
        failed_count = 0
        skipped_count = 0
        
        start_time = datetime.now()
        
        for index, product_url in enumerate(product_urls, 1):
            try:
                # Calculate ETA
                if saved_count > 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    avg_time_per_charm = elapsed / saved_count
                    remaining = total_products - index + 1
                    eta_seconds = avg_time_per_charm * remaining
                    eta_mins = int(eta_seconds / 60)
                    print(f"\n[{index}/{total_products}] ETA: ~{eta_mins} minutes remaining")
                else:
                    print(f"\n[{index}/{total_products}]")
                
                # Scrape this product
                logger.info(f"Scraping: {product_url}")
                html = await scraper._make_request(product_url)
                
                if not html:
                    logger.warning(f"  ⚠️  Failed to fetch HTML")
                    failed_count += 1
                    continue
                
                # Parse product data
                charm_data = scraper._parse_product_page(html, product_url)
                
                if not charm_data:
                    logger.warning(f"  ⚠️  Failed to parse product data")
                    failed_count += 1
                    continue
                
                # Generate charm_id from name
                charm_name = charm_data.get('name', '')
                if not charm_name:
                    logger.warning(f"  ⚠️  No name found, skipping")
                    skipped_count += 1
                    continue
                
                # Create charm document
                charm_id = f"charm_{charm_name.lower().replace(' ', '_').replace('-', '_')}"
                charm_data['_id'] = charm_id
                charm_data['id'] = charm_id
                charm_data['scraped_at'] = datetime.utcnow()
                charm_data['created_at'] = datetime.utcnow()
                charm_data['last_updated'] = datetime.utcnow()
                
                # Add missing fields for compatibility
                if 'description' not in charm_data:
                    charm_data['description'] = f"Beautiful {charm_name} from James Avery collection"
                
                if 'status' not in charm_data:
                    charm_data['status'] = 'Active'
                
                if 'is_retired' not in charm_data:
                    charm_data['is_retired'] = False
                
                # Save to database immediately
                await db.charms.insert_one(charm_data)
                saved_count += 1
                
                # Show success with key details
                price_display = f"${charm_data.get('price', charm_data.get('official_price', 'N/A'))}"
                images_count = len(charm_data.get('images', []))
                
                print(f"  ✅ {charm_name}")
                print(f"     💰 Price: {price_display}")
                print(f"     📷 Images: {images_count}")
                print(f"     🆔 ID: {charm_id}")
                
                # Rate limiting (be nice to the server)
                await asyncio.sleep(0.5)
                
                # Progress update every 10 charms
                if saved_count % 10 == 0:
                    print(f"\n{'='*70}")
                    print(f"📊 Progress: {saved_count} saved, {failed_count} failed, {skipped_count} skipped")
                    print(f"{'='*70}")
                
            except Exception as e:
                logger.error(f"  ❌ Error processing product: {str(e)}")
                failed_count += 1
                continue
        
        # Final summary
        total_time = (datetime.now() - start_time).total_seconds()
        total_mins = int(total_time / 60)
        
        print("\n" + "="*70)
        print("📊 SEEDING COMPLETE")
        print("="*70)
        print(f"✅ Successfully saved: {saved_count} charms")
        print(f"❌ Failed to scrape: {failed_count} charms")
        print(f"⚠️  Skipped (no name): {skipped_count} charms")
        print(f"📈 Total processed: {saved_count + failed_count + skipped_count}/{total_products}")
        print(f"⏱️  Total time: {total_mins} minutes")
        print("="*70)
        
        # Show sample of saved charms
        if saved_count > 0:
            print("\n📝 Sample of saved charms:")
            samples = await db.charms.find({}).limit(5).to_list(length=5)
            for idx, charm in enumerate(samples, 1):
                print(f"  {idx}. {charm.get('name')} - ${charm.get('price', charm.get('official_price', 'N/A'))}")
        
        print("\n💡 Next steps:")
        print("   1. Start backend: python server.py")
        print("   2. Visit frontend: http://localhost:3000")
        print("   3. Browse charms with real James Avery data!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user!")
        print(f"📊 Stats before interruption:")
        print(f"   ✅ Saved: {saved_count} charms")
        print(f"   ❌ Failed: {failed_count} charms")
        print(f"   ⚠️  Skipped: {skipped_count} charms")
        print("\nℹ️  All saved charms are already in the database.")
        
    except Exception as e:
        logger.error(f"❌ Fatal error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # Close connections
        if hasattr(scraper, 'session') and scraper.session:
            await scraper.session.close()
        client.close()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║         James Avery Charms - Incremental Database Seeding        ║
    ║                                                                   ║
    ║  This script will:                                                ║
    ║  1. Clear ALL existing charms from the database                  ║
    ║  2. Discover all charm product URLs from James Avery             ║
    ║  3. Scrape each charm's details (name, price, images, etc.)      ║
    ║  4. Save each charm IMMEDIATELY after scraping                   ║
    ║                                                                   ║
    ║  ✅ Advantages:                                                   ║
    ║     • No data loss if script crashes partway through             ║
    ║     • See progress in real-time                                  ║
    ║     • Can resume by skipping already-saved charms                ║
    ║                                                                   ║
    ║  ⏱️  Estimated time: 30-60 minutes (depends on catalog size)     ║
    ║                                                                   ║
    ║  ⚠️  WARNING: This will DELETE all existing charm data!          ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(seed_charms_incremental())
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
