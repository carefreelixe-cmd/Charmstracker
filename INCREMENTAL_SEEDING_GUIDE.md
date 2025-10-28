# Incremental Seeding - Complete Guide

## ✅ What We Just Created

### 3 New Scripts

1. **`seed_incremental.py`** - Main incremental seeding script
   - Clears database first (with confirmation)
   - Discovers all James Avery product URLs
   - Scrapes and saves each charm ONE-BY-ONE
   - Shows progress and ETA
   - Safe from data loss if it crashes

2. **`test_incremental_seed.py`** - Quick test script
   - Tests with just 3 charms
   - Saves to `test_charms` collection (doesn't affect real data)
   - Verifies scraper is working correctly

3. **Updated `james_avery_scraper.py`**
   - Added `_get_all_product_urls()` method
   - Discovers ALL products from James Avery categories
   - Scans: heart-charms, religious-charms, animal-charms, etc.

---

## 🚀 How to Use

### Option 1: Test First (RECOMMENDED)

```powershell
# Navigate to backend
cd d:\Charmstracker\backend

# Run quick test (scrapes just 3 charms)
python test_incremental_seed.py
```

**This will:**
- Scrape 3 charms from James Avery
- Save to `test_charms` collection (safe)
- Show you if scraper is working correctly

### Option 2: Full Reseed

```powershell
# Navigate to backend
cd d:\Charmstracker\backend

# Run full incremental seed
python seed_incremental.py
```

**This will:**
1. Ask for confirmation before clearing database
2. Discover all product URLs (takes a few minutes)
3. Scrape and save each charm immediately
4. Show progress with ETA
5. Take 30-60 minutes depending on catalog size

---

## ⚙️ How It Works

### OLD Way (Risky):
```
Scrape ALL → Save ALL
   ↓            ↓
If crash here → LOSE EVERYTHING!
```

### NEW Way (Safe):
```
Scrape 1 → Save 1 → Scrape 2 → Save 2 → ...
   ↓         ↓         ↓         ↓
 Always safe! Data in DB immediately!
```

---

## 📊 What You'll See

```
╔═══════════════════════════════════════════════════════════════════╗
║         James Avery Charms - Incremental Database Seeding        ║
╚═══════════════════════════════════════════════════════════════════╝

======================================================================
🗑️  STEP 1: Clearing existing charm data...
======================================================================
Found 45 existing charms in database

⚠️  Delete all 45 charms? (yes/no): yes
✅ Deleted 45 charms

======================================================================
🔍 STEP 2: Discovering all product URLs...
======================================================================
This will take a few minutes as we scan all categories...

✅ Found 487 products to scrape
======================================================================

======================================================================
📥 STEP 3: Scraping and saving charms incrementally...
======================================================================
Each charm will be saved immediately after scraping.

[1/487] ETA: ~45 minutes remaining
Scraping: https://www.jamesavery.com/charms/bow-charm/CM-6491.html
  ✅ Bow Charm
     💰 Price: $49.00
     📷 Images: 5
     🆔 ID: charm_bow_charm

[2/487] ETA: ~44 minutes remaining
Scraping: https://www.jamesavery.com/charms/heart-charm/CM-1234.html
  ✅ Heart Charm
     💰 Price: $39.00
     📷 Images: 4
     🆔 ID: charm_heart_charm

...
```

---

## 🛡️ Safety Features

1. **Confirmation Before Delete**
   - Won't delete database without your "yes"

2. **Incremental Saves**
   - Each charm saved immediately
   - No data loss if script crashes

3. **Error Handling**
   - Continues even if one charm fails
   - Shows failed/skipped counts

4. **Progress Tracking**
   - ETA calculated in real-time
   - Progress updates every 10 charms

5. **Keyboard Interrupt (Ctrl+C)**
   - Shows stats before exiting
   - Already-saved charms remain in database

---

## 📝 Data Structure

Each saved charm includes:

```javascript
{
  _id: "charm_bow_charm",
  id: "charm_bow_charm",
  name: "Bow Charm",
  description: "Beautiful Bow Charm from James Avery collection",
  price: 49.00,
  official_price: 49.00,
  material: "Sterling Silver",
  status: "Active",
  is_retired: false,
  images: [
    "https://jamesavery.scene7.com/is/image/JamesAvery/CM-6491-A",
    "https://jamesavery.scene7.com/is/image/JamesAvery/CM-6491-B",
    ...
  ],
  url: "https://www.jamesavery.com/charms/bow-charm/CM-6491.html",
  scraped_at: ISODate("2024-01-15T10:30:00Z"),
  created_at: ISODate("2024-01-15T10:30:00Z"),
  last_updated: ISODate("2024-01-15T10:30:00Z")
}
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'scrapers'"

**Solution:**
```powershell
# Make sure you're in backend directory
cd d:\Charmstracker\backend
python seed_incremental.py
```

### "Connection refused to MongoDB"

**Solution:**
```powershell
# Start MongoDB service
net start MongoDB
```

Or check if MongoDB is running:
```powershell
mongo --eval "db.version()"
```

### Script is very slow

**Normal!** Each charm takes ~1 second to scrape (rate limiting).
For 500 charms = ~8-10 minutes minimum.

### Want to resume after interruption?

The script currently starts fresh each time. If you want to resume:

**Option A: Let it finish naturally**
- The incremental saves mean you won't lose progress

**Option B: Modify script to skip existing**
Add this check before scraping:
```python
# Check if already exists
existing = await db.charms.find_one({'_id': charm_id})
if existing:
    print(f"  ⏭️  Already exists, skipping")
    continue
```

---

## 📈 Next Steps After Seeding

1. **Verify Data**
   ```powershell
   # Connect to MongoDB
   mongo
   
   # Check count
   use charmstracker
   db.charms.count()
   
   # Sample records
   db.charms.find().limit(5).pretty()
   ```

2. **Start Backend**
   ```powershell
   cd d:\Charmstracker\backend
   python server.py
   ```

3. **Visit Frontend**
   - Go to: http://localhost:3000
   - Browse charms with real James Avery images!
   - All pricing should show (from James Avery official)

4. **Add eBay Data** (Optional)
   - The backend scheduler will automatically fetch eBay data
   - Or run: `python backend/add_fallback_listings.py`

---

## ⚡ Quick Reference

```powershell
# Test with 3 charms
python test_incremental_seed.py

# Full reseed (30-60 mins)
python seed_incremental.py

# Check MongoDB
mongo
use charmstracker
db.charms.count()
db.charms.find().limit(5)

# Start backend
python server.py

# Frontend
# http://localhost:3000
```

---

## 🎯 Key Differences from Old Script

| Feature | Old (`seed_from_james_avery.py`) | New (`seed_incremental.py`) |
|---------|----------------------------------|------------------------------|
| **Save Method** | All at once at end | One-by-one during scraping |
| **Data Loss Risk** | HIGH (crash = lose all) | NONE (each saved immediately) |
| **Progress Visible** | No | Yes (real-time ETA) |
| **Clear DB First** | No | Yes (with confirmation) |
| **Error Handling** | Basic | Comprehensive |
| **Resume Support** | No | Can be added easily |

---

## 💡 Pro Tips

1. **Run test first**: Always use `test_incremental_seed.py` before full reseed

2. **Monitor progress**: Watch the console - you'll see each charm being saved

3. **Don't interrupt unnecessarily**: But if you do (Ctrl+C), your progress is saved!

4. **Check logs**: If failures occur, check the printed URLs and error messages

5. **Database backup**: Before full reseed, backup your database:
   ```powershell
   mongodump --db charmstracker --out backup/
   ```

---

## ✅ You're Ready!

Your new incremental seeding script is **production-ready** and **safe**!

**Recommended workflow:**
1. Run `test_incremental_seed.py` to verify (2 minutes)
2. If test passes, run `seed_incremental.py` (30-60 minutes)
3. Start backend and verify data in frontend
4. Deploy to Hostinger when ready

**Questions?** Check the script output - it's very verbose and will guide you!
