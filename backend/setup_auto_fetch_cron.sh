#!/bin/bash
# Setup cron job to auto-fetch prices every 6 hours

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
SCRIPT_PATH="$SCRIPT_DIR/auto_fetch_all_prices.py"
LOG_PATH="$SCRIPT_DIR/auto_fetch.log"

# Create cron job entry
CRON_JOB="0 */6 * * * cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH") && echo "Cron job already exists" || {
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added successfully!"
    echo "   Runs every 6 hours"
    echo "   Log file: $LOG_PATH"
}

echo ""
echo "Current cron jobs:"
crontab -l | grep -F "$SCRIPT_PATH" || echo "None found"

echo ""
echo "To manually run the script:"
echo "cd $SCRIPT_DIR"
echo "source venv/bin/activate"
echo "python auto_fetch_all_prices.py"
