# Console Logging Guide - Marketplace Data Tracking 🔍

## Overview
Comprehensive console logging has been added to track real-time data fetching from all three marketplace platforms: **eBay**, **Etsy**, and **Poshmark**.

## Where Logging Occurs

### 1. Frontend - CharmDetail Page
**File**: `frontend/src/pages/CharmDetail.jsx`

**What Gets Logged**:
- ✅ Total number of listings found
- 🛒 eBay listing count + sample listing
- 🎨 Etsy listing count + sample listing  
- 👗 Poshmark listing count + sample listing
- 💰 Average price and James Avery price
- 🖼️ Image count and URLs
- ⚠️ Warning if no listings found

**When It Logs**:
- On page load (charm detail view)
- After clicking "Refresh Charm" button
- Auto-refresh every 30 seconds

### 2. Frontend - API Service
**File**: `frontend/src/services/api.js`

**What Gets Logged**:
- 🔍 API request initiated (charm ID)
- ✅ API response received (charm name)
- 🔄 Update request sent to scraper endpoint
- 📡 Endpoint being called

### 3. Backend - Data Aggregator
**File**: `backend/services/data_aggregator.py`

**What Gets Logged**:
- 🔄 Start of data update process
- 📊 Individual listing counts per platform
- 💰 Sample prices from each platform
- 📦 Total aggregated listings
- 💰 Calculated average price

## How to View Logs

### Browser Console (Frontend)
1. Open your site: https://charms.freelixe.com
2. Press **F12** or right-click → **Inspect**
3. Click **Console** tab
4. Navigate to any charm detail page
5. Look for logs with emojis:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📦 CHARM DATA RECEIVED: Cross Charm
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ Total Listings Found: 15
   🛒 eBay: 8 listings
     Sample eBay listing: {...}
   🎨 Etsy: 4 listings
     Sample Etsy listing: {...}
   👗 Poshmark: 3 listings
     Sample Poshmark listing: {...}
   ```

### Server Logs (Backend)
SSH into your server and check backend logs:
```bash
ssh root@31.220.50.205
tail -f /root/charmstracker/backend.log
```

Or check Python logging output:
```bash
journalctl -u charmstracker-api -f
```

## Testing the Logging

### Test 1: View Charm Detail
1. Go to https://charms.freelixe.com
2. Click any charm from the homepage
3. Open browser console (F12)
4. Check for the console logs showing listing counts

### Test 2: Trigger Refresh
1. On a charm detail page
2. Click "Refresh Charm" button
3. Watch console logs show:
   - Update request being sent
   - New data being fetched
   - Platform breakdown of listings

### Test 3: Check Backend Logs
1. SSH to server: `ssh root@31.220.50.205`
2. View logs: `tail -f /root/charmstracker/backend.log`
3. Trigger a refresh from frontend
4. Watch backend logs show scraper activity

## What to Look For

### ✅ Success Indicators
- All three platforms (eBay, Etsy, Poshmark) show listing counts > 0
- Sample listings display price and title
- Average price is calculated
- Images are loaded

### ⚠️ Warning Signs
- Platform shows 0 listings (check if API is working)
- "NO LISTINGS FOUND" message (may need to seed data)
- API errors in console (check API keys in .env)
- Missing images (check image URLs)

## Log Message Reference

| Emoji | Meaning | Location |
|-------|---------|----------|
| 📦 | Charm data package received | Frontend |
| ✅ | Success/completion | Both |
| 🛒 | eBay data | Both |
| 🎨 | Etsy data | Both |
| 👗 | Poshmark data | Both |
| 💰 | Price information | Both |
| 🖼️ | Image data | Frontend |
| 🔍 | API request started | Frontend |
| 🔄 | Update/refresh triggered | Both |
| 📡 | API endpoint info | Frontend |
| ⚠️ | Warning | Both |
| ❌ | Error | Both |
| 📊 | Statistics/counts | Backend |

## Troubleshooting

### No Etsy Listings
Check if Etsy API key is valid:
```bash
# In backend/.env
ETSY_API_KEY=zb44hlacwiz248ya2puy0uiq
```

Test Etsy API directly:
```bash
curl -X GET "https://openapi.etsy.com/v3/application/listings/active?keywords=james+avery&limit=5" \
  -H "x-api-key: zb44hlacwiz248ya2puy0uiq"
```

### No Poshmark Listings
Check if Apify token is valid:
```bash
# In backend/.env
APIFY_API_TOKEN=apify_api_jb1425hlIyOA8j6z2jyJ8g0QHSM1iJ3UziSA
```

Check Apify dashboard: https://console.apify.com

### No eBay Listings
eBay uses web scraping, check:
- Network connectivity
- eBay website not blocking requests
- Rate limiting not exceeded

## Deployment

These logging changes are included in the latest commit. To deploy:

```bash
# On your local machine
git push

# On production server
ssh root@31.220.50.205
cd /root/charmstracker
git pull
pm2 restart charmstracker-api  # or kill and restart uvicorn
```

## Performance Impact

The logging is lightweight and minimal:
- ✅ Only logs on data fetch (not on every render)
- ✅ Uses native console.log (no external libraries)
- ✅ Backend logs at INFO level (can be disabled in production)
- ✅ No performance degradation

To disable verbose logging in production:
```python
# In backend/server.py
logging.basicConfig(level=logging.WARNING)  # Change from INFO
```

## Next Steps

1. ✅ Deploy code to production server
2. ✅ Test console logs in browser
3. ✅ Verify all three platforms return data
4. ✅ Check backend logs for scraper activity
5. ✅ Monitor for any API errors

---

**Last Updated**: January 2025  
**Author**: CharmTracker Development Team
