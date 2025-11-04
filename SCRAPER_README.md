# 🔄 CharmTracker Auto-Scraper System

## What It Does
- ✅ **Automatically scrapes** James Avery charms every 6 hours
- ✅ **No duplicates** - smart logic prevents duplicate data
- ✅ **Updates only changed data** - skips unchanged charms
- ✅ **Two frontend buttons** - manual refresh options

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
python server.py
```

**Look for:**
```
✅ Background scheduler started successfully
🏪 James Avery scraper: every 6 hours
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Visit Any Charm Page
```
http://localhost:3000/charm/charm_enamel_bunny_ears_art_glass_charm
```

**You'll see:**
- "Refresh Charm" button (fast - single charm)
- "Refresh All Data" button (slow - all charms)

---

## 📋 How Duplicate Prevention Works

```python
# For each scraped charm:

# 1. Generate unique ID based on name
charm_id = f"charm_{name.lower().replace(' ', '_')}"

# 2. Check if exists in MongoDB
existing = await db.charms.find_one({'_id': charm_id})

# 3. Smart decision:
if not existing:
    # NEW - Insert charm
    await db.charms.insert_one(charm)
elif data_changed:
    # CHANGED - Update charm
    await db.charms.update_one({'_id': charm_id}, {'$set': new_data})
else:
    # SAME - Skip (no action)
    pass
```

**Result:** MongoDB `_id` uniqueness ensures no duplicates!

---

## 🎯 Key Files

### Backend
- `backend/services/scheduler.py` - Auto-scraper (runs every 6 hours)
- `backend/routes/scraper.py` - API endpoints
- `backend/scrapers/james_avery_scraper.py` - Core scraper logic
- `backend/scrape_and_save.py` - Manual scraper script

### Frontend
- `frontend/src/pages/CharmDetail.jsx` - Refresh buttons
- `frontend/src/services/api.js` - API calls

---

## 🔧 Configuration

### Change Scraper Interval
Edit `backend/services/scheduler.py` (line ~25):
```python
# Current: 6 hours
self.scraper_interval_seconds = 6 * 60 * 60

# Change to 12 hours:
self.scraper_interval_seconds = 12 * 60 * 60

# Change to 3 hours:
self.scraper_interval_seconds = 3 * 60 * 60
```

Then restart backend.

---

## 📊 Monitor Scraping

### Watch Backend Logs
```
🏪 Starting scheduled James Avery scrape
🔍 Finding all James Avery products...
✅ Found 450 products

[1/450] ✅ Saved: Cross Charm          # New
[2/450] ✏️ Updated: Heart Charm        # Changed
[3/450] ⏭️ Skipped (no changes): ...  # Same

📊 SCRAPING SUMMARY
✅ New charms saved: 15
✏️ Existing updated: 230
⏭️ Skipped (no changes): 205
❌ Failed: 0
📦 Total in database: 450
⏱️ Duration: 32.5 minutes
```

### Check API Status
```bash
curl http://localhost:8000/api/scraper/status
```

---

## 🔘 Manual Trigger Options

### Option 1: Frontend Button
1. Go to any charm page
2. Click "Refresh All Data"
3. Wait 30-45 minutes

### Option 2: API Endpoint
```bash
curl -X POST http://localhost:8000/api/scraper/james-avery/scrape
```

### Option 3: Direct Script
```bash
cd backend
python scrape_and_save.py
```

---

## 🐛 Troubleshooting

### Scraper Not Running
```bash
# Check logs for "Background scheduler started"
# If missing, restart backend
cd backend
python server.py
```

### Frontend Buttons Not Working
```bash
# Check browser console for errors
# Verify backend is running
curl http://localhost:8000/api/scraper/status
```

### Duplicates Created (Shouldn't Happen!)
```bash
# Check MongoDB for duplicates
mongosh
use charmstracker
db.charms.aggregate([
  { $group: { _id: "$_id", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
# Should return: []
```

---

## 📝 Environment Variables

Create `.env` file in backend folder:
```env
# MongoDB
MONGO_URL=mongodb://localhost:27017/
DB_NAME=charmstracker

# Scraper Configuration
UPDATE_INTERVAL_HOURS=6
UPDATE_BATCH_SIZE=10

# CORS
CORS_ORIGINS=http://localhost:3000,https://charmstracker.com
```

---

## ✅ Test Script

Test if everything is configured correctly:
```bash
cd backend
python test_scheduler.py
```

**Expected:** All tests pass ✅

---

## 📊 Complete Setup Code

### Backend Scheduler (services/scheduler.py)
```python
class BackgroundScheduler:
    def __init__(self, db):
        self.db = db
        self.aggregator = DataAggregator(db)
        self.running = False
        self.task = None
        self.scraper_task = None
        
        # Scraper runs every 6 hours
        self.scraper_interval_seconds = 6 * 60 * 60
    
    async def _run_james_avery_scraper(self):
        """Run James Avery scraper every 6 hours"""
        while self.running:
            try:
                await self._run_james_avery_scrape()
                await asyncio.sleep(self.scraper_interval_seconds)
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                await asyncio.sleep(1800)  # Wait 30 min on error
    
    async def _run_james_avery_scrape(self):
        """Execute scraper with duplicate prevention"""
        from ..scrapers.james_avery_scraper import JamesAveryScraper
        
        scraper = JamesAveryScraper()
        product_urls = await scraper._get_all_product_urls()
        
        saved = updated = skipped = failed = 0
        
        for url in product_urls:
            # Scrape product
            html = await scraper._make_request(url)
            data = scraper._parse_product_page(html, url)
            
            # Generate unique ID
            name = data['name']
            charm_id = f"charm_{name.lower().replace(' ', '_')}"
            
            # Check if exists
            existing = await self.db.charms.find_one({'_id': charm_id})
            
            if existing:
                # Check if changed
                has_changes = (
                    existing.get('price') != data.get('price') or
                    existing.get('images') != data.get('images')
                )
                
                if has_changes:
                    await self.db.charms.update_one(
                        {'_id': charm_id},
                        {'$set': {...}}  # Update fields
                    )
                    updated += 1
                else:
                    skipped += 1  # No changes
            else:
                # Insert new
                await self.db.charms.insert_one({...})
                saved += 1
        
        logger.info(f"✅ Saved: {saved} | ✏️ Updated: {updated} | ⏭️ Skipped: {skipped}")
```

### Frontend Button (pages/CharmDetail.jsx)
```jsx
const handleRefreshAllData = async () => {
  try {
    setScraperRunning(true);
    await charmAPI.triggerJamesAveryScrape();
    
    alert('🏪 Scraper started! Check back in 30-45 minutes.');
    
    setScraperRunning(false);
  } catch (error) {
    console.error('Error:', error);
    setScraperRunning(false);
  }
};

// In JSX:
<button onClick={handleRefreshAllData} disabled={scraperRunning}>
  <RefreshCw className={scraperRunning ? 'animate-spin' : ''} />
  {scraperRunning ? 'Running...' : 'Refresh All Data'}
</button>
```

### API Endpoint (routes/scraper.py)
```python
@router.post("/james-avery/scrape")
async def trigger_james_avery_scrape(background_tasks: BackgroundTasks):
    """Trigger immediate James Avery scraper"""
    scheduler = get_scheduler()
    
    # Run in background
    background_tasks.add_task(scheduler.trigger_immediate_scrape)
    
    return {
        "message": "James Avery scrape started",
        "status": "processing",
        "expected_duration_minutes": "30-45"
    }
```

### API Client (services/api.js)
```javascript
export const charmAPI = {
  // Trigger James Avery scraper
  triggerJamesAveryScrape: async () => {
    return await apiFetch('/api/scraper/james-avery/scrape', {
      method: 'POST',
    });
  },
  
  // Update single charm
  updateCharm: async (charmId) => {
    return await apiFetch(`/api/scraper/update/${charmId}`, {
      method: 'POST',
    });
  },
};
```

---

## 🎉 Summary

**Your system:**
- ✅ Runs automatically every 6 hours
- ✅ Prevents duplicates (MongoDB `_id` uniqueness)
- ✅ Updates only changed data
- ✅ Skips unchanged data
- ✅ Has manual refresh buttons
- ✅ Fully logged and monitorable

**Just start the backend and frontend - it handles everything else!** 🚀

---

**Questions?** Check backend logs or API status endpoint.
