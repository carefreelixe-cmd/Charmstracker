# Keep Charms Active - Automated Solution

## Problem
When James Avery data scraping runs every 6 hours, some charms are incorrectly marked as "Retired" due to temporary page load issues or missing elements, requiring manual intervention.

## Solution

### 1. Fixed Scraper Logic ✅
**File:** `backend/scrapers/james_avery_scraper.py`

The scraper is now **more conservative** about marking charms as retired:
- ✅ Only marks as "Retired" if explicitly stated on the page with phrases like:
  - "This item has been retired"
  - "Product is retired"
  - "No longer available"
  - "Permanently discontinued"
- ❌ Does NOT mark as retired for:
  - Missing add-to-cart button (could be page loading issue)
  - Temporary out of stock
  - Other temporary issues

### 2. Automated Task - Keep All Charms Active ✅
**File:** `backend/make_all_active.py`

Enhanced with logging for production use. Runs every 6 hours to ensure all charms stay active.

## Setup Instructions

### For Linux/Mac (Cron):
```bash
cd backend
chmod +x setup_make_active_cron.sh
./setup_make_active_cron.sh
```

This creates a cron job that runs every 6 hours (00:00, 06:00, 12:00, 18:00).

### For Windows (Task Scheduler):
```batch
cd backend
REM Run as Administrator
setup_make_active_cron.bat
```

This creates a Windows scheduled task that runs every 6 hours.

## Manual Usage

To manually run the script anytime:

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

python make_all_active.py
```

## Verify Cron Job

### Linux/Mac:
```bash
crontab -l | grep make_all_active
```

### Windows:
```batch
schtasks /Query /TN "CharmsTracker_MakeAllActive" /V
```

## View Logs

### Linux/Mac:
```bash
tail -f backend/make_all_active.log
```

### Windows:
Check Task Scheduler logs or redirect output in the task.

## Summary

✅ **Scraper fixed** - Less aggressive about marking items as retired  
✅ **Automated task** - Runs every 6 hours to reset all charms to Active  
✅ **Cross-platform** - Works on both Linux/Mac and Windows  
✅ **Logging** - All runs are logged for debugging  

Now you don't need to manually run `make_all_active.py` every day!
