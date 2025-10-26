import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_page():
    url = "https://www.jamesavery.com/charms/heart-to-heart-charm/CM-1979.html?dwvar_CM-1979_metal=Sterling%20Silver"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("=" * 70)
            print("ANALYZING JAMES AVERY PRODUCT PAGE")
            print("=" * 70)
            
            # Find ALL images
            all_imgs = soup.find_all('img')
            print(f"\nTotal images found: {len(all_imgs)}")
            
            print("\nAll image URLs:")
            for idx, img in enumerate(all_imgs, 1):
                src = img.get('src', img.get('data-src', img.get('data-zoom-src', 'NO SRC')))
                alt = img.get('alt', 'NO ALT')
                classes = ' '.join(img.get('class', []))
                print(f"\n{idx}. URL: {src[:100]}")
                print(f"   ALT: {alt[:50]}")
                print(f"   CLASSES: {classes[:80]}")
            
            # Look for product-specific divs
            print("\n" + "=" * 70)
            print("Looking for product image containers...")
            print("=" * 70)
            
            containers = soup.find_all('div', class_=lambda x: x and ('product' in str(x).lower() or 'image' in str(x).lower()))
            print(f"\nFound {len(containers)} containers with 'product' or 'image' in class")
            
            for container in containers[:5]:
                classes = ' '.join(container.get('class', []))
                print(f"\nContainer: {classes}")
                imgs_in_container = container.find_all('img')
                print(f"Images inside: {len(imgs_in_container)}")

asyncio.run(debug_page())
