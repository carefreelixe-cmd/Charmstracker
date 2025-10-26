import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json

async def find_all_images():
    url = "https://www.jamesavery.com/charms/bow-charm/CM-6491.html?dwvar_CM-6491_metal=Sterling%20Silver"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            
            print("=" * 80)
            print("FINDING ALL PRODUCT IMAGES")
            print("=" * 80)
            
            # Look for Scene7 viewer config in JavaScript
            # Usually has mediaset or image list
            
            # Pattern 1: Look for s7viewers config
            s7_config = re.search(r's7viewers\.(?:BasicZoomViewer|FlyoutViewer)\(\s*\{[^}]+\}', html, re.DOTALL)
            if s7_config:
                print(f"\nFound S7 Viewer Config:\n{s7_config.group()[:500]}")
            
            # Pattern 2: Look for MediaSet
            mediaset = re.search(r'MediaSet["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
            if mediaset:
                print(f"\nFound MediaSet: {mediaset.group(1)}")
            
            # Pattern 3: Look for zoomView config
            zoomview = re.search(r'zoomView["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
            if zoomview:
                print(f"\nFound ZoomView: {zoomview.group(1)}")
            
            # Pattern 4: Extract all Scene7 image IDs (without query params)
            print("\n" + "=" * 80)
            print("ALL SCENE7 IMAGE IDS:")
            print("=" * 80)
            
            # Find all CM-6491 references (this product code)
            product_images = re.findall(r'https://jamesavery\.scene7\.com/is/image/JamesAvery/([^?&"\'\s]+)', html)
            unique_images = []
            seen = set()
            
            for img_id in product_images:
                # Filter product images (contains CM- or MS_CM-)
                if 'CM-6491' in img_id or 'MS_CM-6491' in img_id:
                    if img_id not in seen:
                        seen.add(img_id)
                        unique_images.append(img_id)
            
            print(f"\nFound {len(unique_images)} unique product images:")
            for idx, img_id in enumerate(unique_images, 1):
                full_url = f"https://jamesavery.scene7.com/is/image/JamesAvery/{img_id}"
                print(f"{idx}. {full_url}")
            
            # Pattern 5: Look for image array in data attributes or script
            print("\n" + "=" * 80)
            print("LOOKING FOR IMAGE ARRAY IN SCRIPTS:")
            print("=" * 80)
            
            # Look for pdpImagesList or similar
            image_list = re.search(r'(?:pdpImagesList|imageList|images)\s*[:=]\s*\[([^\]]+)\]', html)
            if image_list:
                print(f"Found image list: {image_list.group(0)[:300]}...")

asyncio.run(find_all_images())
