# Fix Zero Listings Issue - Debugging Guide

## Problem
When clicking "Fetch Live Prices", the API returns 0 listings even though scrapers exist.

## Root Cause Analysis

The scrapers exist and should work, but there might be:

1. **ScraperAPI Credits** - Out of API calls
2. **AgentQL API Key** - Missing or invalid for Poshmark
3. **Search Query Format** - Not finding results on marketplaces
4. **Timeout Issues** - Scrapers timing out before results return

## Quick Test on Server

### Step 1: SSH into Hostinger
```bash
ssh your_username@your_server_ip
cd ~/Charmstracker/backend
```

### Step 2: Test Scraper Directly
```bash
# Activate Python environment
source venv/bin/activate

# Run test script
python test_scraper_quick.py
```

This will show you:
- ✅ How many listings each platform returns
- ✅ Sample results from each marketplace
- ✅ Average price calculated
- ❌ Any errors from ScraperAPI or AgentQL

### Step 3: Check API Keys

```bash
# Check if API keys are set
cat .env | grep -E "SCRAPER|AGENTQL"
```

You should see:
```
SCRAPERAPI_KEY=be8b8d16e40d4f8d81658ba7b2cc4b34
AGENTQL_API_KEY=your_agentql_key_here
```

### Step 4: Check ScraperAPI Credits

1. Go to: https://dashboard.scraperapi.com
2. Login with account linked to key: `be8b8d16e40d4f8d81658ba7b2cc4b34`
3. Check remaining API credits
4. If out of credits, that's why you get 0 listings!

### Step 5: Check Backend Logs

```bash
# Watch live logs
sudo journalctl -u charmstracker-api -f
```

Then click "Fetch Live Prices" and watch for errors like:
- `❌ ScraperAPI returned status 403` = No credits or invalid key
- `❌ AgentQL error` = AgentQL key missing/invalid
- `❌ Error fetching page` = Network/timeout issue

## Common Issues & Fixes

### Issue 1: ScraperAPI Out of Credits ⚠️
**Symptoms:**
- API returns 200 OK but 0 listings
- Logs show "ScraperAPI returned status 403" or "401"

**Fix:**
1. Check dashboard: https://dashboard.scraperapi.com
2. Upgrade plan or wait for monthly reset
3. Alternative: Use free proxies (less reliable)

### Issue 2: AgentQL Key Missing
**Symptoms:**
- eBay and Etsy work (5-10 listings each)
- Poshmark returns 0 listings
- Log shows "AgentQL not available"

**Fix:**
```bash
# Add to .env file
echo "AGENTQL_API_KEY=your_key_here" >> .env

# Restart API
sudo systemctl restart charmstracker-api
```

### Issue 3: Search Query Not Finding Results
**Symptoms:**
- All platforms return 0 listings
- No errors in logs
- ScraperAPI has credits

**Fix:**
The query format might be wrong. Test different formats:
```python
# Current format
"James Avery Jesus Loves Me Charm"

# Try alternatives:
"Jesus Loves Me Charm"  # Without brand
"james avery charm"  # Generic
```

Edit `backend/routes/scraper.py` line 247:
```python
# Change from:
all_listings = await loop.run_in_executor(None, scraper.scrape_all, f"James Avery {charm_name}")

# To (test):
all_listings = await loop.run_executor(None, scraper.scrape_all, charm_name)
```

### Issue 4: Timeout Before Results Return
**Symptoms:**
- Frontend shows success alert but 0 listings
- Backend logs show scraping started but no completion

**Fix:**
Increase timeout in `backend/scrapers/scraperapi_client.py`:
```python
# Line 41: Change from timeout=60 to timeout=120
response = requests.get(self.base_url, params=payload, timeout=120)
```

## Testing Each Scraper Individually

### Test Etsy Only:
```python
cd ~/Charmstracker/backend
python -c "
from scrapers.scraperapi_client import ScraperAPIClient
scraper = ScraperAPIClient()
results = scraper.scrape_etsy('James Avery Jesus Loves Me Charm')
print(f'Etsy Results: {len(results)}')
for r in results[:3]:
    print(f'  {r[\"title\"]} - \${r[\"price\"]}')
"
```

### Test eBay Only:
```python
python -c "
from scrapers.scraperapi_client import ScraperAPIClient
scraper = ScraperAPIClient()
results = scraper.scrape_ebay('James Avery Jesus Loves Me Charm')
print(f'eBay Results: {len(results)}')
for r in results[:3]:
    print(f'  {r[\"title\"]} - \${r[\"price\"]}')
"
```

### Test Poshmark (AgentQL):
```bash
# Poshmark requires AgentQL and Playwright
python test_agentql_james_avery.py
```

## Manual API Test

Test the endpoint directly:

```bash
# Get a charm ID first
curl https://charms.freelixe.com/api/charms | jq -r '.charms[0].id'

# Save the ID and test fetch-live-prices
curl -X POST https://charms.freelixe.com/api/scraper/fetch-live-prices/YOUR_CHARM_ID | jq .
```

This will show the exact API response, including any errors.

## Quick Fixes to Try Now

### Fix 1: Use ScraperAPI for All Platforms (Skip AgentQL)
Edit `backend/scrapers/scraperapi_client.py` around line 241:

```python
def scrape_poshmark(self, charm_name: str) -> List[Dict]:
    """Scrape Poshmark using ScraperAPI instead of AgentQL"""
    try:
        logger.info(f"👗 [POSHMARK] Scraping: {charm_name}")
        
        # Use direct ScraperAPI scraping instead
        url = f"https://poshmark.com/search?query={charm_name.replace(' ', '+')}"
        html = self.fetch_page(url, render_js=True)
        
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        listings = []
        
        # Parse Poshmark HTML (simplified)
        # ... add parsing logic here
        
        return listings
        
    except Exception as e:
        logger.error(f"❌ [POSHMARK] Error: {e}")
        return []
```

### Fix 2: Return Sample Data if Scraping Fails (Temporary)
Add fallback data in `backend/routes/scraper.py` around line 250:

```python
all_listings = await loop.run_in_executor(None, scraper.scrape_all, f"James Avery {charm_name}")

# TEMPORARY: If no results, return sample data to test frontend
if not all_listings:
    logger.warning("⚠️ No scraper results, using sample data")
    all_listings = [
        {
            'platform': 'etsy',
            'marketplace': 'Etsy',
            'title': f'{charm_name} (Sample)',
            'price': 45.00,
            'url': 'https://www.etsy.com',
            'condition': 'New',
            'seller': 'Sample Seller',
            'image_url': ''
        }
    ]
```

This helps test if the issue is scraping or frontend rendering.

## Next Steps

1. **Run test_scraper_quick.py** to see which platforms work
2. **Check ScraperAPI credits** at dashboard
3. **Check backend logs** for errors
4. **Test API endpoint** directly with curl
5. **Report back** which platform returns 0 and any error messages

The test script will tell us exactly where the problem is!
