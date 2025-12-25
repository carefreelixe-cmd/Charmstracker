#!/bin/bash
# Quick test of fetch-live-prices endpoint on Hostinger server

echo "================================================"
echo "Testing Fetch Live Prices Endpoint"
echo "================================================"
echo ""

# Get first charm ID from database
echo "🔍 Getting a charm ID from database..."
CHARM_ID=$(mongosh --quiet --eval "use charmstracker; db.charms.findOne({}, {_id: 1}).id" | tail -1 | tr -d '"')

if [ -z "$CHARM_ID" ]; then
    echo "❌ Could not get charm ID from database"
    echo "Try manually: mongosh"
    echo "  > use charmstracker"
    echo "  > db.charms.findOne({}, {_id: 1, name: 1})"
    exit 1
fi

echo "✅ Found charm ID: $CHARM_ID"
echo ""

# Test the endpoint
echo "📡 Testing endpoint..."
echo "POST https://charms.freelixe.com/api/scraper/fetch-live-prices/$CHARM_ID"
echo ""

# Make the API call
RESPONSE=$(curl -s -X POST "https://charms.freelixe.com/api/scraper/fetch-live-prices/$CHARM_ID" \
    -H "Content-Type: application/json" \
    -w "\nHTTP_STATUS:%{http_code}")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "📊 Response Status: $HTTP_STATUS"
echo ""

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ SUCCESS - Endpoint is working!"
    echo ""
    echo "Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    
    # Extract counts
    TOTAL=$(echo "$BODY" | grep -o '"total_listings":[0-9]*' | cut -d: -f2)
    ETSY=$(echo "$BODY" | grep -o '"etsy":{"count":[0-9]*' | grep -o '[0-9]*$')
    EBAY=$(echo "$BODY" | grep -o '"ebay":{"count":[0-9]*' | grep -o '[0-9]*$')
    POSHMARK=$(echo "$BODY" | grep -o '"poshmark":{"count":[0-9]*' | grep -o '[0-9]*$')
    
    echo "Summary:"
    echo "  Total Listings: $TOTAL"
    echo "  🎨 Etsy: $ETSY"
    echo "  🛒 eBay: $EBAY"
    echo "  👗 Poshmark: $POSHMARK"
    
    if [ "$TOTAL" = "0" ]; then
        echo ""
        echo "⚠️  WARNING: 0 listings returned!"
        echo ""
        echo "Check:"
        echo "1. ScraperAPI credits: https://dashboard.scraperapi.com"
        echo "2. Backend logs: sudo journalctl -u charmstracker-api -n 50"
        echo "3. Run scraper test: python backend/test_scraper_quick.py"
    fi
    
else
    echo "❌ ERROR - Endpoint returned $HTTP_STATUS"
    echo ""
    echo "Response:"
    echo "$BODY"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if API is running: sudo systemctl status charmstracker-api"
    echo "2. Check logs: sudo journalctl -u charmstracker-api -n 50"
    echo "3. Test API health: curl https://charms.freelixe.com/api/"
fi

echo ""
echo "================================================"
