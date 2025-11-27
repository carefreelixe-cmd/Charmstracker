"""
Background Task Scheduler for CharmTracker
Automatically updates charm data on schedule
Runs James Avery scraper every 6 hours with duplicate prevention
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Optional
import os

from .data_aggregator import DataAggregator

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Manages scheduled background tasks"""
    
    def __init__(self, db):
        self.db = db
        self.aggregator = DataAggregator(db)
        self.running = False
        self.task = None
        self.scraper_task = None
        
        # Configuration
        self.update_interval_hours = int(os.getenv('UPDATE_INTERVAL_HOURS', '6'))
        self.update_time = os.getenv('UPDATE_TIME', '02:00')  # Default 2 AM
        self.batch_size = int(os.getenv('UPDATE_BATCH_SIZE', '10'))
        
        # James Avery scraper interval (6 hours = 21600 seconds)
        self.scraper_interval_seconds = 6 * 60 * 60  # 6 hours
    
    async def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        self.scraper_task = asyncio.create_task(self._run_james_avery_scraper())
        logger.info("🚀 Background scheduler started")
        logger.info(f"📅 Marketplace updates: every {self.update_interval_hours} hours")
        logger.info(f"🏪 James Avery scraper: every 6 hours")
    
    async def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.scraper_task:
            self.scraper_task.cancel()
            try:
                await self.scraper_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._update_cycle()
                
                # Wait for next update interval
                await asyncio.sleep(self.update_interval_hours * 3600)
                
            except asyncio.CancelledError:
                logger.info("Scheduler task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                # Wait before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def _update_cycle(self):
        """Run a complete update cycle"""
        try:
            logger.info("Starting scheduled update cycle")
            start_time = datetime.utcnow()
            
            # Get charms that need updating (oldest first)
            charms = await self.db.charms.find().sort("last_updated", 1).to_list(1000)
            
            total_charms = len(charms)
            logger.info(f"Found {total_charms} charms to update")
            
            # Update in batches
            success_count = 0
            fail_count = 0
            
            for i in range(0, total_charms, self.batch_size):
                batch = charms[i:i + self.batch_size]
                
                logger.info(f"Processing batch {i//self.batch_size + 1}")
                
                # Update batch in parallel
                tasks = [
                    self.aggregator.update_charm_data(charm['id'])
                    for charm in batch
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        fail_count += 1
                    elif result:
                        success_count += 1
                    else:
                        fail_count += 1
                
                # Rate limiting between batches
                if i + self.batch_size < total_charms:
                    await asyncio.sleep(10)  # 10 seconds between batches
            
            # Log results
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Update cycle complete: {success_count} success, "
                f"{fail_count} failed in {duration:.1f}s"
            )
            
            # Store update statistics
            await self.db.update_stats.insert_one({
                "started_at": start_time,
                "completed_at": datetime.utcnow(),
                "duration_seconds": duration,
                "total_charms": total_charms,
                "success_count": success_count,
                "fail_count": fail_count
            })
            
        except Exception as e:
            logger.error(f"Error in update cycle: {str(e)}")
    
    async def _run_james_avery_scraper(self):
        """Run James Avery scraper every 6 hours with duplicate prevention"""
        logger.info("🏪 James Avery scraper scheduler started")
        
        # Wait 1 minute before first run
        await asyncio.sleep(60)
        
        while self.running:
            try:
                logger.info("="*70)
                logger.info("🏪 Starting scheduled James Avery scrape (6-hour interval)")
                logger.info("="*70)
                
                await self._run_james_avery_scrape()
                
                logger.info("="*70)
                logger.info(f"✅ James Avery scrape complete. Next run in 6 hours")
                logger.info("="*70)
                
                # Wait 6 hours before next run
                await asyncio.sleep(self.scraper_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("James Avery scraper task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in James Avery scraper loop: {str(e)}")
                # Wait 30 minutes before retrying on error
                await asyncio.sleep(1800)
    
    async def _run_james_avery_scrape(self):
        """Execute James Avery scraper with duplicate prevention"""
        try:
            from scrapers.james_avery_scraper import JamesAveryScraper
            
            scraper = JamesAveryScraper()
            
            # Get all product URLs
            logger.info("🔍 Finding all James Avery products...")
            product_urls = await scraper._get_all_product_urls()
            total = len(product_urls)
            logger.info(f"✅ Found {total} products")
            
            if total == 0:
                logger.warning("⚠️ No products found from James Avery")
                return
            
            saved = 0
            updated = 0
            skipped = 0
            failed = 0
            start_time = datetime.utcnow()
            
            for i, url in enumerate(product_urls, 1):
                try:
                    # Rate limiting
                    if i > 1:
                        await asyncio.sleep(0.5)  # 500ms between requests
                    
                    # Scrape product
                    html = await scraper._make_request(url)
                    if not html:
                        failed += 1
                        continue
                    
                    data = scraper._parse_product_page(html, url)
                    if not data or not data.get('name'):
                        failed += 1
                        continue
                    
                    # Create charm document
                    name = data['name']
                    charm_id = f"charm_{name.lower().replace(' ', '_').replace('-', '_')}"
                    
                    # Format images
                    images = data.get('images', [])
                    formatted_images = []
                    for img_url in images:
                        if 'scene7.com' in img_url and '?' not in img_url:
                            img_url = f"{img_url}?wid=800&hei=800&fmt=jpeg&qlt=90"
                        formatted_images.append(img_url)
                    
                    # Check if charm exists
                    existing = await self.db.charms.find_one({'_id': charm_id})
                    
                    if existing:
                        # Check if data has changed
                        has_changes = (
                            existing.get('name') != name or
                            existing.get('price') != data.get('price') or
                            existing.get('official_price') != data.get('official_price') or
                            existing.get('status') != data.get('status') or
                            existing.get('images') != formatted_images
                        )
                        
                        if has_changes:
                            # Update only if data changed
                            await self.db.charms.update_one(
                                {'_id': charm_id},
                                {'$set': {
                                    'name': name,
                                    'description': data.get('description', f"Beautiful {name} from James Avery"),
                                    'price': data.get('price', data.get('official_price')),
                                    'official_price': data.get('official_price'),
                                    'material': data.get('material', 'Sterling Silver'),
                                    'images': formatted_images,
                                    'url': data.get('url', url),
                                    'sku': data.get('sku'),
                                    'status': data.get('status', 'Active'),
                                    'is_retired': data.get('status') == 'Retired',
                                    'scraped_at': datetime.utcnow(),
                                    'last_updated': datetime.utcnow()
                                }}
                            )
                            updated += 1
                            if i % 50 == 0:
                                logger.info(f"[{i}/{total}] ✏️  Updated: {name}")
                        else:
                            skipped += 1
                            if i % 50 == 0:
                                logger.info(f"[{i}/{total}] ⏭️  Skipped (no changes): {name}")
                    else:
                        # Insert new charm
                        charm = {
                            '_id': charm_id,
                            'id': charm_id,
                            'name': name,
                            'description': data.get('description', f"Beautiful {name} from James Avery"),
                            'price': data.get('price', data.get('official_price')),
                            'official_price': data.get('official_price'),
                            'material': data.get('material', 'Sterling Silver'),
                            'images': formatted_images,
                            'url': data.get('url', url),
                            'sku': data.get('sku'),
                            'status': data.get('status', 'Active'),
                            'is_retired': data.get('status') == 'Retired',
                            'avg_price': data.get('price', data.get('official_price', 50)),
                            'price_change_7d': 0.0,
                            'price_change_30d': 0.0,
                            'price_change_90d': 0.0,
                            'popularity': 75,
                            'listings': [],
                            'price_history': [],
                            'related_charm_ids': [],
                            'scraped_at': datetime.utcnow(),
                            'created_at': datetime.utcnow(),
                            'last_updated': datetime.utcnow()
                        }
                        await self.db.charms.insert_one(charm)
                        saved += 1
                        if i % 50 == 0:
                            logger.info(f"[{i}/{total}] ✅ Saved: {name}")
                    
                    # Progress update every 100 items
                    if i % 100 == 0:
                        elapsed = (datetime.utcnow() - start_time).total_seconds() / 60
                        logger.info(f"Progress: {i}/{total} | Saved: {saved} | Updated: {updated} | Skipped: {skipped} | Failed: {failed} | Time: {elapsed:.1f}min")
                
                except Exception as e:
                    failed += 1
                    if i % 100 == 0:
                        logger.error(f"Error processing product: {str(e)[:100]}")
                    continue
            
            # Final summary
            duration = (datetime.utcnow() - start_time).total_seconds() / 60
            total_in_db = await self.db.charms.count_documents({})
            
            logger.info("")
            logger.info("="*70)
            logger.info("📊 SCRAPING SUMMARY")
            logger.info("="*70)
            logger.info(f"✅ New charms saved: {saved}")
            logger.info(f"✏️  Existing updated: {updated}")
            logger.info(f"⏭️  Skipped (no changes): {skipped}")
            logger.info(f"❌ Failed: {failed}")
            logger.info(f"📦 Total in database: {total_in_db}")
            logger.info(f"⏱️  Duration: {duration:.1f} minutes")
            logger.info("="*70)
            
            if hasattr(scraper, 'session') and scraper.session:
                await scraper.session.close()
            
        except Exception as e:
            logger.error(f"❌ Error in James Avery scrape: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def trigger_immediate_update(self, charm_id: Optional[str] = None):
        """Trigger an immediate update outside the schedule"""
        try:
            if charm_id:
                logger.info(f"Triggering immediate update for charm {charm_id}")
                success = await self.aggregator.update_charm_data(charm_id)
                return {"success": success, "charm_id": charm_id}
            else:
                logger.info("Triggering immediate update for all charms")
                stats = await self.aggregator.update_all_charms()
                return stats
                
        except Exception as e:
            logger.error(f"Error in immediate update: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def trigger_immediate_scrape(self):
        """Trigger an immediate James Avery scrape outside the schedule"""
        try:
            logger.info("🏪 Triggering immediate James Avery scrape...")
            await self._run_james_avery_scrape()
            return {"success": True, "message": "James Avery scrape completed"}
        except Exception as e:
            logger.error(f"❌ Error in immediate scrape: {str(e)}")
            return {"success": False, "error": str(e)}


# Global scheduler instance
_scheduler_instance: Optional[BackgroundScheduler] = None


def get_scheduler(db) -> BackgroundScheduler:
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = BackgroundScheduler(db)
    return _scheduler_instance


async def start_scheduler(db):
    """Start the global scheduler"""
    scheduler = get_scheduler(db)
    await scheduler.start()


async def stop_scheduler():
    """Stop the global scheduler"""
    if _scheduler_instance:
        await _scheduler_instance.stop()