# Deploy Make All Charms Active to Hostinger

## Quick Setup on Hostinger Server

### Step 1: Upload Files to Server
Make sure these files are on your Hostinger server:
- `backend/make_all_active.py` ✅
- `backend/setup_make_active_cron.sh` ✅

### Step 2: SSH into Hostinger
```bash
ssh your_username@your_server_ip
cd ~/domains/charmstracker.com/public_html/backend
# OR wherever your backend folder is located
```

### Step 3: Make Script Executable
```bash
chmod +x setup_make_active_cron.sh
```

### Step 4: Run Setup Script
```bash
./setup_make_active_cron.sh
```

This will create a cron job that runs every 6 hours.

### Step 5: Verify Cron Job
```bash
crontab -l
```

You should see:
```
0 */6 * * * cd /home/YOUR_PATH/backend && /home/YOUR_PATH/backend/venv/bin/python /home/YOUR_PATH/backend/make_all_active.py >> /home/YOUR_PATH/backend/make_all_active.log 2>&1
```

## Manual Commands

### Run immediately (test):
```bash
cd ~/domains/charmstracker.com/public_html/backend
source venv/bin/activate
python make_all_active.py
```

### View logs:
```bash
tail -f ~/domains/charmstracker.com/public_html/backend/make_all_active.log
```

### Remove cron job:
```bash
crontab -e
# Delete the line with make_all_active.py
# Save and exit
```

## Alternative: Manual Cron Setup

If the script doesn't work, set up manually:

1. Edit crontab:
```bash
crontab -e
```

2. Add this line (replace paths with your actual paths):
```
0 */6 * * * cd /home/YOUR_USERNAME/domains/charmstracker.com/public_html/backend && /home/YOUR_USERNAME/domains/charmstracker.com/public_html/backend/venv/bin/python /home/YOUR_USERNAME/domains/charmstracker.com/public_html/backend/make_all_active.py >> /home/YOUR_USERNAME/domains/charmstracker.com/public_html/backend/make_all_active.log 2>&1
```

3. Save and exit (Ctrl+X, then Y, then Enter)

## Schedule

The script runs at:
- 00:00 (midnight)
- 06:00 (6 AM)
- 12:00 (noon)
- 18:00 (6 PM)

Every day, keeping all charms Active!

## Troubleshooting

### Check if cron is running:
```bash
sudo service cron status
```

### Test the script manually:
```bash
cd ~/domains/charmstracker.com/public_html/backend
python make_all_active.py
```

### Check Python path:
```bash
which python
# Use this path in your cron job if different
```

### Check MongoDB connection:
Make sure `.env` file has correct MONGO_URL on the server.

## What This Does

✅ Runs every 6 hours automatically  
✅ Resets all charms to "Active" status  
✅ Prevents charms from staying "Retired" incorrectly  
✅ Logs all runs for debugging  
✅ Works alongside the 6-hour price scraping  

## Desktop vs Server

❌ **Windows scheduled task** = Only for testing on your desktop  
✅ **Linux cron job** = Production on Hostinger server  

Make sure to set this up on Hostinger, not your local machine!
