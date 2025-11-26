"""
Scraper API Routes for CharmTracker
Provides endpoints to trigger and monitor data updates
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Optional
from datetime import datetime
import logging

from ..services.data_aggregator import DataAggregator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


def get_database():
    """Get database instance from server"""
    from ..server import db
    return db


def get_scheduler():
    """Get scheduler instance"""
    from ..services.scheduler import _scheduler_instance
    return _scheduler_instance


def get_aggregator():
    """Get data aggregator instance"""
    db = get_database()
    return DataAggregator(db)


@router.post("/update/{charm_id}")
async def update_charm(
    charm_id: str,
    background_tasks: BackgroundTasks
):
    """
    Trigger an update for a specific charm
    Runs in background to avoid blocking
    """
    try:
        # Run update in background
        aggregator = get_aggregator()
        background_tasks.add_task(aggregator.update_charm_data, charm_id)
        
        return {
            "message": f"Update started for charm {charm_id}",
            "status": "processing",
            "charm_id": charm_id
        }
        
    except Exception as e:
        logger.error(f"Error triggering update for {charm_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-all")
async def update_all_charms(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = Query(None, ge=1, le=100)
):
    """
    Trigger update for all charms (or limited number)
    Runs in background
    """
    try:
        aggregator = get_aggregator()
        background_tasks.add_task(aggregator.update_all_charms, limit)
        
        return {
            "message": f"Update started for {'all' if not limit else limit} charms",
            "status": "processing",
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error triggering update-all: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scraper_status():
    """Get status of scraper service and scheduler"""
    try:
        db = get_database()
        scheduler = get_scheduler()
        
        # Get last update times for charms
        recent_updates = await db.charms.find(
            {},
            {"id": 1, "name": 1, "last_updated": 1}
        ).sort("last_updated", -1).limit(10).to_list(10)
        
        # Count total charms
        total_charms = await db.charms.count_documents({})
        
        # Count charms updated in last 24 hours
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_count = await db.charms.count_documents({
            "last_updated": {"$gte": cutoff}
        })
        
        # Get scheduler status
        scheduler_status = {
            "running": scheduler.running if scheduler else False,
            "update_interval_hours": scheduler.update_interval_hours if scheduler else None,
            "scraper_interval_hours": 6 if scheduler else None,
            "next_auto_scrape": "Every 6 hours" if (scheduler and scheduler.running) else "Not scheduled"
        }
        
        return {
            "status": "operational",
            "total_charms": total_charms,
            "updated_last_24h": recent_count,
            "scheduler": scheduler_status,
            "recent_updates": [
                {
                    "id": charm["id"],
                    "name": charm["name"],
                    "last_updated": charm.get("last_updated", "").isoformat() if charm.get("last_updated") else None
                }
                for charm in recent_updates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting scraper status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/james-avery/scrape")
async def trigger_james_avery_scrape(background_tasks: BackgroundTasks):
    """
    Trigger immediate James Avery scraper
    Scrapes all charms from James Avery website
    No duplicates - updates existing or creates new
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler:
            raise HTTPException(
                status_code=503, 
                detail="Scheduler not initialized. Please restart the backend server."
            )
        
        # Run scrape in background
        background_tasks.add_task(scheduler.trigger_immediate_scrape)
        
        return {
            "message": "James Avery scrape started",
            "status": "processing",
            "info": "This will scrape all charms from James Avery. Check logs for progress. Takes ~30-45 minutes.",
            "expected_duration_minutes": "30-45"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering James Avery scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace-check/{charm_name}")
async def check_marketplace_availability(charm_name: str):
    """
    Check if a charm is available on each marketplace
    Quick check without full update
    """
    try:
        from ..scrapers.ebay_scraper import ebay_scraper
        from ..scrapers.etsy_scraper import etsy_scraper
        from ..scrapers.poshmark_scraper import poshmark_scraper
        
        # Quick search on each platform (limit 5)
        import asyncio
        tasks = [
            ebay_scraper.search_charm(charm_name, limit=5),
            etsy_scraper.search_charm(charm_name, limit=5),
            poshmark_scraper.search_charm(charm_name, limit=5),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Helper function to extract listing count
        def get_listing_count(result):
            if isinstance(result, Exception):
                return 0
            elif isinstance(result, dict):
                return len(result.get('listings', []))
            elif isinstance(result, list):
                return len(result)
            return 0
        
        return {
            "charm_name": charm_name,
            "availability": {
                "ebay": {
                    "available": get_listing_count(results[0]) > 0,
                    "listing_count": get_listing_count(results[0])
                },
                "etsy": {
                    "available": get_listing_count(results[1]) > 0,
                    "listing_count": get_listing_count(results[1])
                },
                "poshmark": {
                    "available": get_listing_count(results[2]) > 0,
                    "listing_count": get_listing_count(results[2])
                }
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking marketplace availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-live-prices/{charm_id}")
async def fetch_live_prices(charm_id: str):
    """
    Fetch live prices from Etsy, eBay, and Poshmark using ScraperAPI
    Updates the database with fresh marketplace data
    """
    try:
        from ..scrapers.scraperapi_client import ScraperAPIClient
        
        # Get charm from database
        db = get_database()
        charm = await db.charms.find_one({"_id": charm_id})
        
        if not charm:
            raise HTTPException(status_code=404, detail="Charm not found")
        
        charm_name = charm.get('name', '')
        logger.info(f"📡 Fetching live prices with ScraperAPI for: {charm_name}")
        
        # Use ScraperAPI client (runs synchronously in thread)
        import asyncio
        scraper = ScraperAPIClient()
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        all_listings = await loop.run_in_executor(None, scraper.scrape_all, f"James Avery {charm_name}")
        
        # Organize by platform
        etsy_listings = [l for l in all_listings if l.get('platform') == 'etsy']
        ebay_listings = [l for l in all_listings if l.get('platform') == 'ebay']
        poshmark_listings = [l for l in all_listings if l.get('platform') == 'poshmark']
        
        # Calculate average price
        prices = [l['price'] for l in all_listings if l['price'] > 0]
        average_price = sum(prices) / len(prices) if prices else charm.get('average_price', 0)
        
        # Extract images
        images = [l['image_url'] for l in all_listings if l.get('image_url')]
        
        # Update database
        update_data = {
            'listings': all_listings,
            'average_price': round(average_price, 2),
            'last_updated': datetime.utcnow(),
            'listing_count': len(all_listings)
        }
        
        # Add images if we found new ones
        if images:
            existing_images = charm.get('images', [])
            all_images = list(set(existing_images + images[:5]))  # Add top 5 new images
            update_data['images'] = all_images
        
        await db.charms.update_one(
            {"_id": charm_id},
            {"$set": update_data}
        )
        
        logger.info(f"✅ Updated {charm_name}: {len(all_listings)} listings, avg ${average_price:.2f}")
        
        return {
            "success": True,
            "charm_id": charm_id,
            "charm_name": charm_name,
            "summary": {
                "etsy": {
                    "count": len(etsy_listings),
                    "listings": etsy_listings
                },
                "ebay": {
                    "count": len(ebay_listings),
                    "listings": ebay_listings
                },
                "poshmark": {
                    "count": len(poshmark_listings),
                    "listings": poshmark_listings
                }
            },
            "total_listings": len(all_listings),
            "average_price": round(average_price, 2),
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching live prices with AgentQL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
