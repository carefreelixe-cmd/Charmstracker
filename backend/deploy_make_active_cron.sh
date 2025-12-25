#!/bin/bash
# Quick Deploy: Setup Make All Active Cron on Hostinger
# Run this on your Hostinger server

echo "==========================================="
echo "HOSTINGER: Setup Make All Active Cron Job"
echo "==========================================="
echo ""

# Find backend directory
if [ -d "backend" ]; then
    cd backend
elif [ -d "~/domains/charmstracker.com/public_html/backend" ]; then
    cd ~/domains/charmstracker.com/public_html/backend
else
    echo "ERROR: Cannot find backend directory"
    echo "Please cd to your project root first"
    exit 1
fi

CURRENT_DIR=$(pwd)
echo "Working in: $CURRENT_DIR"
echo ""

# Make setup script executable
if [ -f "setup_make_active_cron.sh" ]; then
    chmod +x setup_make_active_cron.sh
    echo "✅ Made setup_make_active_cron.sh executable"
else
    echo "❌ ERROR: setup_make_active_cron.sh not found"
    exit 1
fi

# Run the setup
echo ""
echo "Running setup script..."
echo ""
./setup_make_active_cron.sh

echo ""
echo "==========================================="
echo "✅ SETUP COMPLETE"
echo "==========================================="
echo ""
echo "The cron job will run every 6 hours to keep all charms active."
echo ""
echo "Next run times: 00:00, 06:00, 12:00, 18:00"
echo ""
echo "To verify:"
echo "  crontab -l | grep make_all_active"
echo ""
echo "To view logs:"
echo "  tail -f $CURRENT_DIR/make_all_active.log"
echo ""
