# Debug Live Price Fetching Issue

## Problem
When clicking "Fetch Live Prices" button, the prices are fetched but not showing in the charm details page.

## What I Fixed

### 1. Enhanced Console Logging ✅
Added detailed console logs to track the data flow:
- `frontend/src/pages/CharmDetail.jsx` - Added logs to `handleFetchLivePrices()` and `fetchCharmDetail()`
- Now logs the full API response and database refresh

### 2. Better Error Handling ✅
- Shows error details in console
- Alert message now says "Check console for details"

## How to Debug

### Step 1: Open Browser Console
Press F12 in your browser and go to the Console tab.

### Step 2: Click "Fetch Live Prices"
Watch the console logs. You should see:

```
🤖 FETCHING LIVE PRICES (Running in background)...
   Charm: [charm name]
   Scraping Etsy, eBay, Poshmark with AgentQL AI...
✅ Live prices fetched successfully!
📊 FULL RESULT: {result object}
   🎨 Etsy: X listings
   🛒 eBay: X listings
   👗 Poshmark: X listings
   💰 Average: $XX.XX
🔄 Refreshing charm data from database...
🔄 Fetching charm detail for ID: xxx
📦 Raw charm data received: {data}
   - Listings count: X
   - Average price: X
   - Last updated: ...
✅ Charm data refreshed! New data should now be visible.
```

### Step 3: Check for Errors

#### If you see "❌ Error fetching live prices"
- Check the error details in console
- Verify API endpoint is working: `https://api.charmstracker.com/api/scraper/fetch-live-prices/{charm_id}`
- Check backend logs: `cd ~/Charmstracker/backend && tail -f api.log`

#### If listings count is 0 after fetching
- Backend may have failed to scrape
- Check ScraperAPI credits/limits
- Verify MongoDB is updating correctly

#### If data doesn't update on page
- Check if `setCharm(updatedData)` is being called
- Verify the component is re-rendering
- Look for React state issues

## Test on Server

### SSH into Hostinger
```bash
ssh your_username@your_server_ip
cd ~/Charmstracker/backend
```

### Check API Logs
```bash
# Watch real-time logs
tail -f api.log

# Or check systemd logs
sudo journalctl -u charmstracker-api -f
```

### Test Backend Endpoint Directly
```bash
# Get a charm ID first
curl https://api.charmstracker.com/api/charms | grep -o '"id":"[^"]*"' | head -1

# Then fetch live prices
curl -X POST https://api.charmstracker.com/api/scraper/fetch-live-prices/{CHARM_ID}
```

## Common Issues & Solutions

### Issue 1: CORS Error
**Symptom:** Console shows CORS error  
**Solution:** Check nginx configuration, ensure API subdomain is set up correctly

### Issue 2: 500 Internal Server Error
**Symptom:** Backend returns 500 error  
**Solution:** Check backend logs for Python errors, likely ScraperAPI or MongoDB issue

### Issue 3: Data fetched but not displayed
**Symptom:** Console shows success but page doesn't update  
**Solution:** 
- Verify `charm` state is being updated
- Check if PriceComparison component is receiving new props
- Force refresh the page after fetching

### Issue 4: Listings show as 0
**Symptom:** API returns 0 listings  
**Solution:**
- Check ScraperAPI account balance
- Verify search query is correct (should be "James Avery {charm_name}")
- Test scrapers individually

## Quick Fix Commands

### Rebuild and Deploy Frontend
```bash
cd ~/Charmstracker/frontend
npm run build
# Copy to appropriate location for your server
```

### Restart Backend
```bash
sudo systemctl restart charmstracker-api
sudo systemctl status charmstracker-api
```

### Check Database
```bash
# Connect to MongoDB
mongosh

# Use your database
use charmstracker

# Check a charm's listings
db.charms.findOne({}, {name: 1, listings: 1, average_price: 1, last_updated: 1})
```

## Console Logs to Look For

✅ **Success Path:**
```
🤖 FETCHING LIVE PRICES
✅ Live prices fetched successfully!
📊 FULL RESULT: {...}
🔄 Refreshing charm data from database...
📦 Raw charm data received: {...}
✅ Charm data refreshed!
```

❌ **Error Path:**
```
❌ Error fetching live prices: [error]
❌ Error details: [details]
```

## Next Steps

1. Open browser console (F12)
2. Click "Fetch Live Prices" button
3. Copy all console logs
4. Share the logs to identify the exact issue

The enhanced logging will show exactly where the process is failing!
