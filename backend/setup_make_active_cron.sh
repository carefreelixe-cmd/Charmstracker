#!/bin/bash
# Setup cron job to make all charms active every 6 hours
# This prevents charms from being incorrectly marked as retired

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
SCRIPT_PATH="$SCRIPT_DIR/make_all_active.py"
LOG_PATH="$SCRIPT_DIR/make_all_active.log"

# Create cron job entry - runs every 6 hours
CRON_JOB="0 */6 * * * cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

echo "================================================"
echo "Setting up Make All Charms Active Cron Job"
echo "================================================"
echo ""
echo "This will run make_all_active.py every 6 hours to ensure"
echo "all charms stay active (not incorrectly marked as retired)"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "make_all_active.py" > /dev/null; then
    echo "⚠️  Cron job already exists!"
    echo ""
    echo "Current cron job:"
    crontab -l | grep -F "make_all_active.py"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing cron job."
        exit 0
    fi
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "make_all_active.py" | crontab -
    echo "Old cron job removed."
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✅ Cron job added successfully!"
echo ""
echo "Schedule: Every 6 hours (0, 6, 12, 18 hours)"
echo "Script: $SCRIPT_PATH"
echo "Log file: $LOG_PATH"
echo ""
echo "================================================"
echo "Current cron jobs for this project:"
echo "================================================"
crontab -l | grep -E "(make_all_active|auto_fetch)" || echo "None found"
echo ""
echo "================================================"
echo "To manually test the script:"
echo "================================================"
echo "cd $SCRIPT_DIR"
echo "source venv/bin/activate"
echo "python make_all_active.py"
echo ""
echo "================================================"
echo "To view logs:"
echo "================================================"
echo "tail -f $LOG_PATH"
echo ""
