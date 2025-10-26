import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json

async def analyze_page():
    url = "https://www.jamesavery.com/charms/bow-charm/CM-6491.html?dwvar_CM-6491_metal=Sterling%20Silver"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("=" * 80)
            print("ANALYZING BOW CHARM PAGE")
            print("=" * 80)
            
            # Method 1: Look for JSON-LD structured data
            print("\n1. JSON-LD Structured Data:")
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld:
                try:
                    data = json.loads(json_ld.string)
                    print(f"   Found JSON-LD: {json.dumps(data, indent=2)[:500]}...")
                    if 'image' in data:
                        print(f"   Image in JSON-LD: {data['image']}")
                except:
                    print("   Failed to parse JSON-LD")
            
            # Method 2: Look for og:image
            print("\n2. Open Graph Images:")
            og_images = soup.find_all('meta', property='og:image')
            for img in og_images:
                print(f"   {img.get('content')}")
            
            # Method 3: Look for s7staticimage divs
            print("\n3. Scene7 Static Images:")
            s7_divs = soup.find_all('div', class_='s7staticimage')
            print(f"   Found {len(s7_divs)} s7staticimage divs")
            for idx, div in enumerate(s7_divs[:5], 1):
                imgs = div.find_all('img')
                print(f"\n   Div {idx} contains {len(imgs)} images:")
                for img in imgs:
                    src = img.get('src', '')
                    if src and 'scene7.com' in src:
                        print(f"      {src}")
            
            # Method 4: Look for all scene7 image URLs in the HTML
            print("\n4. All Scene7 URLs in HTML:")
            scene7_urls = re.findall(r'https://jamesavery\.scene7\.com/is/image/[^"\'\s]+', html)
            unique_urls = list(set(scene7_urls))
            print(f"   Found {len(unique_urls)} unique Scene7 URLs:")
            for idx, url in enumerate(unique_urls[:10], 1):
                # Clean URL (remove query params for uniqueness check)
                base_url = url.split('?')[0]
                print(f"   {idx}. {base_url}")
            
            # Method 5: Look for data-image attributes
            print("\n5. Images with data-image or data-src attributes:")
            data_imgs = soup.find_all(['img', 'div', 'a'], attrs={'data-image': True})
            data_imgs += soup.find_all(['img', 'div', 'a'], attrs={'data-src': True})
            for img in data_imgs[:10]:
                data_img = img.get('data-image', img.get('data-src', ''))
                if 'scene7' in data_img or 'jamesavery' in data_img:
                    print(f"   {data_img}")
            
            # Method 6: Look for thumbnail carousel
            print("\n6. Looking for thumbnail carousel:")
            carousel = soup.find('div', class_=re.compile(r'carousel|thumbnail|gallery'))
            if carousel:
                print(f"   Found carousel: {carousel.get('class')}")
                thumbs = carousel.find_all('img')
                print(f"   Contains {len(thumbs)} thumbnail images")

asyncio.run(analyze_page())
