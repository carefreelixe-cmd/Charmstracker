# 🔄 What Runs When You Click "Refresh All Data"

## Flow of Execution

```
User clicks "Refresh All Data" button
    ↓
frontend/src/pages/CharmDetail.jsx (handleRefreshAllData function)
    ↓
frontend/src/services/api.js (triggerJamesAveryScrape function)
    ↓
POST /api/scraper/james-avery/scrape
    ↓
backend/routes/scraper.py (trigger_james_avery_scrape endpoint)
    ↓
backend/services/scheduler.py (trigger_immediate_scrape function)
    ↓
backend/services/scheduler.py (_run_james_avery_scrape function)
    ↓
backend/scrapers/james_avery_scraper.py (JamesAveryScraper class)
    ↓
MongoDB (charms collection - save/update/skip)
```

## Files Involved (In Order)

### 1. Frontend Button Click
**File:** `frontend/src/pages/CharmDetail.jsx`

```jsx
const handleRefreshAllData = async () => {
  try {
    setScraperRunning(true);
    await charmAPI.triggerJamesAveryScrape();  // ← Calls API
    
    alert('🏪 James Avery scraper started! Check back in 30-45 minutes.');
    setScraperRunning(false);
  } catch (error) {
    console.error('Error:', error);
    setScraperRunning(false);
  }
};
```

### 2. API Call
**File:** `frontend/src/services/api.js`

```javascript
export const charmAPI = {
  triggerJamesAveryScrape: async () => {
    return await apiFetch('/api/scraper/james-avery/scrape', {
      method: 'POST',
    });
  },
};
```

### 3. Backend API Endpoint
**File:** `backend/routes/scraper.py`

```python
@router.post("/james-avery/scrape")
async def trigger_james_avery_scrape(background_tasks: BackgroundTasks):
    """Trigger immediate James Avery scraper"""
    scheduler = get_scheduler()
    
    if not scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    # Run scrape in background
    background_tasks.add_task(scheduler.trigger_immediate_scrape)  # ← Calls scheduler
    
    return {
        "message": "James Avery scrape started",
        "status": "processing"
    }
```

### 4. Scheduler Trigger
**File:** `backend/services/scheduler.py`

```python
async def trigger_immediate_scrape(self):
    """Trigger an immediate James Avery scrape"""
    try:
        logger.info("🏪 Triggering immediate James Avery scrape...")
        await self._run_james_avery_scrape()  # ← Runs the scraper
        return {"success": True, "message": "James Avery scrape completed"}
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}
```

### 5. Main Scraper Function
**File:** `backend/services/scheduler.py`

```python
async def _run_james_avery_scrape(self):
    """Execute James Avery scraper with duplicate prevention"""
    from ..scrapers.james_avery_scraper import JamesAveryScraper
    
    scraper = JamesAveryScraper()
    
    # Get all product URLs
    product_urls = await scraper._get_all_product_urls()  # ← Fetch URLs
    
    saved = updated = skipped = failed = 0
    
    for i, url in enumerate(product_urls, 1):
        try:
            # Scrape product
            html = await scraper._make_request(url)  # ← Get HTML
            data = scraper._parse_product_page(html, url)  # ← Parse data
            
            # Generate unique ID
            name = data['name']
            charm_id = f"charm_{name.lower().replace(' ', '_').replace('-', '_')}"
            
            # Format images
            images = data.get('images', [])
            formatted_images = []
            for img_url in images:
                if 'scene7.com' in img_url and '?' not in img_url:
                    img_url = f"{img_url}?wid=800&hei=800&fmt=jpeg&qlt=90"
                formatted_images.append(img_url)
            
            # Check if exists
            existing = await self.db.charms.find_one({'_id': charm_id})
            
            if existing:
                # Check if data changed
                has_changes = (
                    existing.get('name') != name or
                    existing.get('price') != data.get('price') or
                    existing.get('images') != formatted_images
                )
                
                if has_changes:
                    # UPDATE
                    await self.db.charms.update_one(
                        {'_id': charm_id},
                        {'$set': {
                            'name': name,
                            'price': data.get('price'),
                            'images': formatted_images,
                            'last_updated': datetime.utcnow()
                        }}
                    )
                    updated += 1
                else:
                    # SKIP (no changes)
                    skipped += 1
            else:
                # INSERT NEW
                charm = {
                    '_id': charm_id,
                    'id': charm_id,
                    'name': name,
                    'price': data.get('price'),
                    'images': formatted_images,
                    'created_at': datetime.utcnow(),
                    'last_updated': datetime.utcnow()
                }
                await self.db.charms.insert_one(charm)
                saved += 1
            
        except Exception as e:
            failed += 1
            continue
    
    # Log summary
    logger.info(f"✅ Saved: {saved} | ✏️ Updated: {updated} | ⏭️ Skipped: {skipped} | ❌ Failed: {failed}")
```

### 6. James Avery Scraper
**File:** `backend/scrapers/james_avery_scraper.py`

```python
class JamesAveryScraper:
    async def _get_all_product_urls(self):
        """Get all product URLs from James Avery"""
        # Scrape category pages
        # Return list of product URLs
        return product_urls
    
    async def _make_request(self, url):
        """Make HTTP request to get product page HTML"""
        async with self.session.get(url) as response:
            return await response.text()
    
    def _parse_product_page(self, html, url):
        """Parse product page HTML to extract data"""
        # Parse HTML using BeautifulSoup
        # Extract: name, price, images, description, etc.
        return {
            'name': name,
            'price': price,
            'images': images,
            'description': description,
            ...
        }
```

## Summary

**When you click "Refresh All Data":**

1. ✅ Frontend button triggers API call
2. ✅ API endpoint receives request
3. ✅ Scheduler's `trigger_immediate_scrape()` is called
4. ✅ `_run_james_avery_scrape()` executes
5. ✅ `JamesAveryScraper` fetches all product URLs
6. ✅ For each URL:
   - Fetch HTML
   - Parse product data
   - Check if charm exists
   - INSERT new / UPDATE changed / SKIP unchanged
7. ✅ Save to MongoDB
8. ✅ Log results

**Key Files:**
- `frontend/src/pages/CharmDetail.jsx` - Button
- `frontend/src/services/api.js` - API call
- `backend/routes/scraper.py` - API endpoint
- `backend/services/scheduler.py` - Main scraper logic
- `backend/scrapers/james_avery_scraper.py` - James Avery scraping

**Result:** All charms updated, no duplicates!
