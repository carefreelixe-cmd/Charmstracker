"""
Poshmark Scraper for CharmTracker
Uses Apify API to fetch real-time listings and pricing data from Poshmark
Documentation: https://apify.com/piotrv1001/poshmark-listings-scraper
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import aiohttp
import asyncio
import os
import re
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PoshmarkScraper:
    """Poshmark scraper using Apify API"""
    
    def __init__(self):
        self.api_token = os.getenv('APIFY_API_TOKEN', '')
        self.actor_id = os.getenv('APIFY_POSHMARK_ACTOR_ID', 'piotrv1001/poshmark-listings-scraper')
        self.base_url = "https://api.apify.com/v2"
        self.poshmark_url = "https://poshmark.com"
        
        if not self.api_token or self.api_token == 'your_apify_token_here':
            logger.warning("Apify API token not configured. Get one from https://console.apify.com/account/integrations")
            self.use_api = False
        else:
            self.use_api = True
        
    async def search_charm(
        self, 
        charm_name: str, 
        limit: int = 20
    ) -> List[Dict]:
        """
        Search Poshmark for a specific charm using Apify API
        Returns list of listings with prices and details
        """
        if not self.use_api:
            logger.warning("Apify API not configured, returning empty results")
            return []
            
        try:
            search_query = f"James Avery {charm_name}"
            # Build Poshmark search URL
            search_url = f"{self.poshmark_url}/search?query={search_query.replace(' ', '%20')}&department=Jewelry"
            
            logger.info(f"Searching Poshmark via Apify for: {charm_name}")
            
            # Start Apify actor
            run_id = await self._start_apify_actor(search_url)
            if not run_id:
                return []
            
            # Wait for results
            results = await self._get_apify_results(run_id, timeout=60)
            
            # Parse and format results
            listings = self._parse_apify_results(results, limit)
            logger.info(f"Found {len(listings)} Poshmark listings")
            
            return listings
                        
        except Exception as e:
            logger.error(f"Error searching Poshmark for {charm_name}: {str(e)}")
            return []
    
    async def _start_apify_actor(self, search_url: str) -> Optional[str]:
        """Start Apify actor and return run ID"""
        try:
            url = f"{self.base_url}/acts/{self.actor_id}/runs"
            
            input_data = {
                "searchUrls": [search_url]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=input_data, headers=headers) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        logger.error(f"Apify API error: {response.status} - {error_text}")
                        return None
                    
                    data = await response.json()
                    run_id = data.get('data', {}).get('id')
                    logger.info(f"Apify actor started: {run_id}")
                    return run_id
                    
        except Exception as e:
            logger.error(f"Error starting Apify actor: {str(e)}")
            return None
    
    async def _get_apify_results(self, run_id: str, timeout: int = 60) -> List[Dict]:
        """Wait for Apify actor to finish and get results"""
        try:
            dataset_url = f"{self.base_url}/actor-runs/{run_id}/dataset/items"
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            # Poll for completion
            for _ in range(timeout):
                await asyncio.sleep(1)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(dataset_url, headers=headers) as response:
                        if response.status == 200:
                            results = await response.json()
                            if results:
                                logger.info(f"Got {len(results)} results from Apify")
                                return results
            
            logger.warning("Apify actor timed out")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Apify results: {str(e)}")
            return []
    
    def _parse_apify_results(self, results: List[Dict], limit: int) -> List[Dict]:
        """Parse Apify actor results into our format"""
        listings = []
        
        for item in results[:limit]:
            try:
                # Extract price
                price_str = item.get('price', '0')
                price = 0.0
                
                if isinstance(price_str, (int, float)):
                    price = float(price_str)
                elif isinstance(price_str, str):
                    price_match = re.search(r'([\d,]+\.?\d*)', price_str.replace('$', ''))
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))
                
                if price <= 0:
                    continue
                
                # Extract other fields
                title = item.get('title', '')
                url = item.get('link', '')
                image_url = item.get('image', '')
                seller = item.get('seller', '')
                brand = item.get('brand', '')
                size = item.get('size', '')
                old_price = item.get('oldPrice', '')
                
                # Determine condition
                condition = 'Pre-owned'
                if 'new' in title.lower() or 'nwt' in title.lower():
                    condition = 'New with Tags'
                
                listing = {
                    'platform': 'Poshmark',
                    'title': title,
                    'price': price,
                    'url': url,
                    'condition': condition,
                    'image_url': image_url,
                    'seller': seller,
                    'brand': brand,
                    'size': size,
                    'shipping': 7.97,  # Poshmark standard shipping
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                if listing['price'] > 0 and listing['url']:
                    listings.append(listing)
                    
            except Exception as e:
                logger.debug(f"Error parsing Apify result: {str(e)}")
                continue
        
        return listings


# Initialize scraper instance
poshmark_scraper = PoshmarkScraper()