"""
eBay API Client for CharmTracker
Uses eBay's Finding and Shopping APIs for real-time data
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EbayAPIClient:
    """eBay API client for fetching real-time listing data"""
    
    def __init__(self):
        self.app_id = os.getenv('EBAY_APP_ID')
        self.cert_id = os.getenv('EBAY_CERT_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID')
        self.finding_url = 'https://svcs.ebay.com/services/search/FindingService/v1'
        self.shopping_url = 'https://open.api.ebay.com/shopping'
        
        if not all([self.app_id, self.cert_id, self.dev_id]):
            raise ValueError("Missing eBay API credentials")
    
    async def search_listings(self, charm_name: str) -> List[Dict]:
        """
        Search for active listings of a specific charm
        Returns normalized listing data
        """
        try:
            params = {
                'OPERATION-NAME': 'findItemsAdvanced',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'REST-PAYLOAD': 'true',
                'keywords': f'James Avery {charm_name}',
                'categoryId': '164333',  # Charms & Charm Bracelets
                'itemFilter(0).name': 'Seller',
                'itemFilter(0).value': 'JamesAvery',  # Official store
                'itemFilter(1).name': 'ListingType',
                'itemFilter(1).value': 'FixedPrice',
                'sortOrder': 'StartTimeNewest',
                'paginationInput.entriesPerPage': 100
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.finding_url, params=params) as response:
                    data = await response.json()
                    
                    if 'findItemsAdvancedResponse' not in data:
                        logger.error(f"Invalid eBay API response: {data}")
                        return []
                    
                    items = data['findItemsAdvancedResponse'][0].get('searchResult', [{}])[0].get('item', [])
                    
                    listings = []
                    for item in items:
                        try:
                            listing = {
                                'platform': 'eBay',
                                'price': float(item['sellingStatus'][0]['currentPrice'][0]['__value__']),
                                'url': item['viewItemURL'][0],
                                'condition': item['condition'][0]['conditionDisplayName'],
                                'seller': item['sellerInfo'][0]['sellerUserName'][0],
                                'scraped_at': datetime.utcnow(),
                                'title': item['title'][0],
                                'item_id': item['itemId'][0],
                                'listing_type': 'Fixed Price' if item.get('listingInfo', [{}])[0].get('listingType', [''])[0] == 'FixedPrice' else 'Auction',
                                'end_time': datetime.strptime(item['listingInfo'][0]['endTime'][0], '%Y-%m-%dT%H:%M:%S.%fZ'),
                                'shipping_cost': float(item.get('shippingInfo', [{}])[0].get('shippingServiceCost', [{'__value__': '0.0'}])[0]['__value__'])
                            }
                            listings.append(listing)
                        except (KeyError, IndexError) as e:
                            logger.warning(f"Error parsing eBay listing: {str(e)}")
                            continue
                    
                    return listings
                    
        except Exception as e:
            logger.error(f"Error fetching eBay listings: {str(e)}")
            return []
    
    async def get_completed_listings(self, charm_name: str, days: int = 30) -> List[Dict]:
        """
        Get completed listings for historical price analysis
        """
        try:
            params = {
                'OPERATION-NAME': 'findCompletedItems',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'REST-PAYLOAD': 'true',
                'keywords': f'James Avery {charm_name}',
                'categoryId': '164333',
                'itemFilter(0).name': 'SoldItemsOnly',
                'itemFilter(0).value': 'true',
                'sortOrder': 'EndTimeSoonest',
                'paginationInput.entriesPerPage': 100
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.finding_url, params=params) as response:
                    data = await response.json()
                    
                    if 'findCompletedItemsResponse' not in data:
                        logger.error(f"Invalid eBay API response: {data}")
                        return []
                    
                    items = data['findCompletedItemsResponse'][0].get('searchResult', [{}])[0].get('item', [])
                    cutoff_date = datetime.utcnow() - timedelta(days=days)
                    
                    completed = []
                    for item in items:
                        try:
                            end_time = datetime.strptime(item['listingInfo'][0]['endTime'][0], '%Y-%m-%dT%H:%M:%S.%fZ')
                            if end_time < cutoff_date:
                                continue
                                
                            listing = {
                                'platform': 'eBay',
                                'price': float(item['sellingStatus'][0]['currentPrice'][0]['__value__']),
                                'end_time': end_time,
                                'condition': item['condition'][0]['conditionDisplayName'],
                                'url': item['viewItemURL'][0],
                                'item_id': item['itemId'][0]
                            }
                            completed.append(listing)
                        except (KeyError, IndexError) as e:
                            logger.warning(f"Error parsing completed eBay listing: {str(e)}")
                            continue
                    
                    return completed
                    
        except Exception as e:
            logger.error(f"Error fetching completed eBay listings: {str(e)}")
            return []