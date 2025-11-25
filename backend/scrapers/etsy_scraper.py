"""
Etsy Scraper for CharmTracker
Uses Etsy API v3 to fetch real-time listings and pricing data
Documentation: https://developer.etsy.com/documentation/reference
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EtsyScraper:
    """Etsy scraper using official API v3"""
    
    def __init__(self):
        self.api_key = os.getenv('ETSY_API_KEY', '')
        self.base_url = "https://openapi.etsy.com/v3"
        
        if not self.api_key:
            logger.warning("Etsy API key not configured. Get one from https://www.etsy.com/developers/")
            self.use_api = False
        else:
            self.use_api = True
    
    async def search_charm(
        self, 
        charm_name: str, 
        limit: int = 20
    ) -> List[Dict]:
        """
        Search Etsy for a specific charm using API v3
        Returns list of listings with prices and details
        """
        if not self.use_api:
            logger.warning("Etsy API not configured, returning empty results")
            return []
            
        try:
            query = f"james avery {charm_name}"
            url = f"{self.base_url}/application/listings/active"
            
            params = {
                'keywords': query,
                'limit': limit,
                'sort_on': 'relevancy',
                'includes': 'Images,Shop'
            }
            
            headers = {
                'x-api-key': self.api_key,
                'Accept': 'application/json'
            }
            
            logger.info(f"Searching Etsy API for: {charm_name}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Etsy API error: {response.status} - {error_text}")
                        return []
                    
                    data = await response.json()
                    results = data.get('results', [])
                    
                    listings = []
                    for item in results:
                        try:
                            listing = self._parse_api_listing(item)
                            if listing:
                                listings.append(listing)
                        except Exception as e:
                            logger.debug(f"Error parsing Etsy listing: {str(e)}")
                            continue
                    
                    logger.info(f"Found {len(listings)} Etsy listings")
                    return listings
                    
        except Exception as e:
            logger.error(f"Error searching Etsy: {str(e)}")
            return []
    
    def _parse_api_listing(self, item: Dict) -> Optional[Dict]:
        """Parse Etsy API listing response"""
        try:
            # Extract price (Etsy returns price in smallest currency unit)
            price_data = item.get('price', {})
            amount = price_data.get('amount', 0)
            divisor = price_data.get('divisor', 100)
            price = float(amount) / float(divisor)
            
            if price <= 0:
                return None
            
            # Extract listing URL
            listing_id = item.get('listing_id', '')
            url = f"https://www.etsy.com/listing/{listing_id}"
            
            # Extract image URL
            images = item.get('images', [])
            image_url = images[0].get('url_570xN', '') if images else ""
            
            # Extract shop info
            shop = item.get('shop', {})
            seller_name = shop.get('shop_name', 'Unknown')
            
            # Determine condition
            condition = "Handmade"
            title = item.get('title', '')
            if 'vintage' in title.lower():
                condition = "Vintage"
            elif 'new' in title.lower():
                condition = "New"
            
            return {
                'platform': 'Etsy',
                'title': title,
                'price': price,
                'url': url,
                'condition': condition,
                'image_url': image_url,
                'seller': seller_name,
                'shipping': 0.0,  # Would need additional API call for shipping
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing Etsy API listing: {str(e)}")
            return None
    
    async def get_listing_details(self, listing_id: str) -> Optional[Dict]:
        """
        Get detailed information from a specific listing using API
        """
        if not self.use_api:
            return None
            
        try:
            url = f"{self.base_url}/application/listings/{listing_id}"
            
            headers = {
                'x-api-key': self.api_key,
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    item = data.get('result', {})
                    
                    return {
                        "description": item.get('description', ''),
                        "tags": item.get('tags', []),
                        "materials": item.get('materials', []),
                        "quantity": item.get('quantity', 0)
                    }
                    
        except Exception as e:
            logger.error(f"Error getting Etsy listing details: {str(e)}")
            return None


# Create singleton instance for import
etsy_scraper = EtsyScraper()


# Testing function
async def test_etsy_scraper():
    """Test the Etsy scraper"""
    scraper = EtsyScraper()
    results = await scraper.search_charm("cross charm", limit=5)
    
    print(f"\n✅ Found {len(results)} Etsy listings:")
    for listing in results:
        print(f"  • {listing['title'][:50]}... - ${listing['price']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_etsy_scraper())