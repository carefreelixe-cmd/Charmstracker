#!/bin/bash

# Script to fix all charms status to Active on production server

echo "======================================"
echo "Fix All Charms to Active Status"
echo "======================================"
echo ""

# Navigate to project directory
cd ~/Charmstracker/backend || exit 1

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the status check and fix script
echo ""
echo "Running status check and fix..."
python check_status_and_fix.py

echo ""
echo "======================================"
echo "Done! All charms should now be Active"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Verify by visiting: https://charmstracker.com"
echo "2. Check any charm detail page"
echo "3. Status should show 'Active' instead of 'Retired'"
