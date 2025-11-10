# Fix: "Refresh All Data" 404 Error

## Problem
When clicking "Refresh All Data" button on the charm detail page, you get:
```
Failed to load resource: the server responded with a status of 404 ()
API Error (/api/scraper/james-avery/scrape): Error: Not Found
```

## Root Cause
The frontend was calling `/api/scraper/james-avery/scrape` endpoint, but this endpoint is NOT available on the production server. This route exists in the code but hasn't been deployed to the live server yet.

### Available Routes on Production:
- ✅ `/api/scraper/status` (GET)
- ✅ `/api/scraper/update/{charm_id}` (POST)
- ✅ `/api/scraper/update-all` (POST)
- ✅ `/api/scraper/marketplace-check/{charm_name}` (GET)
- ❌ `/api/scraper/james-avery/scrape` (POST) - **NOT DEPLOYED**

## Solution Applied
Changed the frontend to use the existing `/api/scraper/update-all` endpoint instead, which serves the same purpose of refreshing data for all charms.

### Files Modified:

#### 1. `frontend/src/services/api.js`
**Changed:** The `triggerJamesAveryScrape()` function now calls `/api/scraper/update-all`

```javascript
// OLD (404 error):
triggerJamesAveryScrape: async () => {
  return await apiFetch('/api/scraper/james-avery/scrape', {
    method: 'POST',
  });
},

// NEW (works):
triggerJamesAveryScrape: async () => {
  return await apiFetch('/api/scraper/update-all', {
    method: 'POST',
  });
},
```

#### 2. `frontend/src/pages/CharmDetail.jsx`
**Changed:** Updated user-facing messages to be more accurate

```javascript
// Updated the alert message
alert('🔄 Data refresh started! This will update all charm data from marketplace sources. Check back in a few minutes for updated data.');

// Updated button tooltip
title="Update all charms from marketplace sources"

// Updated auto-update info text
<strong>Auto-Update:</strong> Data automatically refreshes from marketplace sources. Use the buttons above to manually trigger updates.
```

## Next Steps

### Option 1: Deploy the Fixed Frontend (Recommended)
```bash
cd E:\Charmstracker\frontend
npm run build
# Then deploy the build folder to your hosting
```

### Option 2: Deploy the Backend Route (Future Enhancement)
If you want to use the original `/api/scraper/james-avery/scrape` endpoint:
1. The route already exists in `backend/routes/scraper.py` (line 136)
2. Restart/redeploy the backend server to register this route
3. Revert the frontend changes to use the original endpoint

## Testing
After deploying the frontend, test by:
1. Go to any charm detail page
2. Click "Refresh All Data" button
3. Should see: "🔄 Data refresh started! This will update all charm data..."
4. No 404 errors in console

## Technical Notes
- The `/api/scraper/update-all` endpoint works similarly to the james-avery scraper
- It updates all charms in the database with fresh marketplace data
- Runs in background, doesn't block the UI
- No duplicates created, only updates existing records

## Verification Commands
Check available routes:
```powershell
Invoke-WebRequest -Uri "https://charms.freelixe.com/openapi.json" -Method GET
```

Test the endpoint:
```powershell
Invoke-WebRequest -Uri "https://charms.freelixe.com/api/scraper/update-all" -Method POST
```
