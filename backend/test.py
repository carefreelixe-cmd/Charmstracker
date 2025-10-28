#!/usr/bin/env python3
"""
scrape_jamesavery_charms.py

Scrapes product listings and product pages from https://www.jamesavery.com/charms
Saves results to results.json and downloads images into an 'images/' folder.

Requirements:
    pip install requests beautifulsoup4 tqdm

Usage:
    python scrape_jamesavery_charms.py

Configuration:
    - MAX_PAGES: max listing pages to attempt (set None to keep going until no "next" is found)
    - SLEEP_BETWEEN_REQUESTS: polite delay (seconds)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import os
import re
from tqdm import tqdm
import sys

# --- Config ---
BASE_URL = "https://www.jamesavery.com/charms"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JamesAveryScraper/1.0; +https://example.com/bot)"
}
OUTPUT_JSON = "results.json"
IMAGES_DIR = "images"
MAX_PAGES = None  # set to an int to limit pages (useful for development)
SLEEP_BETWEEN_REQUESTS = 1.0  # seconds

# --- Helpers ---
session = requests.Session()
session.headers.update(HEADERS)

def check_robots_allowed(base_url, user_agent=HEADERS["User-Agent"], path="/charms"):
    """Check robots.txt to see if scraping the path is allowed."""
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        r = session.get(robots_url, timeout=15)
    except Exception as e:
        print(f"[WARN] Could not fetch robots.txt ({robots_url}): {e}")
        return True  # be conservative: allow but we warn
    if r.status_code != 200:
        print(f"[WARN] robots.txt returned status {r.status_code}. Proceeding but check site policy.")
        return True
    txt = r.text
    # Very simple robots parser: check Disallow lines for our user agent or '*' entries
    ua_re = re.compile(r"User-agent:\s*(\S+)", re.I)
    disallow_re = re.compile(r"Disallow:\s*(\S*)", re.I)
    sections = txt.split("\n\n")
    applicable_disallows = []
    for sec in sections:
        lines = [l.strip() for l in sec.splitlines() if l.strip()]
        if not lines:
            continue
        ua = None
        disallows = []
        for line in lines:
            m = ua_re.match(line)
            if m:
                ua = m.group(1)
            m2 = disallow_re.match(line)
            if m2:
                disallows.append(m2.group(1))
        if ua in (user_agent, "*", None):
            applicable_disallows += disallows
    # If any disallow matches our path -> block
    for d in applicable_disallows:
        if d == "":
            continue
        # treat simple prefix matching
        if path.startswith(d):
            print(f"[robots.txt] Disallow rule matching path '{d}'")
            return False
    return True

def get_soup(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"[ERROR] Failed to GET {url}: {e}")
        return None

def parse_listing_page(soup, base_url):
    """
    Given a listing page soup, return:
        - products: list of dicts with 'title' and 'product_url' and possible price/thumbnail
        - next_page_url: url or None
    """
    products = []
    # The site may use grid items; try common patterns
    # Look for product cards with anchor links
    # Flexible selectors: search for links that appear to go to product detail pages under /products or similar
    anchors = soup.select("a[href]")
    seen = set()
    for a in anchors:
        href = a.get("href")
        if not href:
            continue
        # Normalize link
        full = urljoin(base_url, href)
        # Heuristics: a product URL often contains '/product' or '/products' or '/charms/' and has non-empty text
        if re.search(r"/product|/products|/charms/.+|/products/.+", full, re.I):
            title = (a.get_text(strip=True) or a.get("aria-label") or "").strip()
            # try to find price inside or sibling
            price = None
            # look for element with class containing 'price'
            parent = a.parent
            price_tag = None
            # search nearby for price spans
            for candidate in a.find_all_next(string=True, limit=6):
                text = candidate.strip()
                if re.search(r"\$\s*\d", text):
                    price_tag = text
                    break
            if not title:
                # maybe there's an img alt
                img = a.find("img")
                if img and img.get("alt"):
                    title = img.get("alt").strip()
            key = (full, title)
            if full not in seen and title:
                seen.add(full)
                products.append({
                    "title": title,
                    "product_url": full,
                    "price": price_tag
                })
    # Attempt to detect "next page" link
    next_page = None
    # Common pagination selectors
    next_link = soup.select_one("a[rel=next], a.pagination__next, a.next, li.next a")
    if next_link and next_link.get("href"):
        next_page = urljoin(base_url, next_link.get("href"))
    else:
        # fallback: look for numeric pagination and find current page then next
        pag_links = soup.select("a[href]")
        for a in pag_links:
            txt = a.get_text(strip=True).lower()
            if txt in ("next", "›", "»"):
                next_page = urljoin(base_url, a.get("href"))
                break
    return products, next_page

def parse_product_page(soup, url):
    """
    Extract product details from a product page soup.
    Returns a dict with keys: title, sku, price, description, attributes (dict), images (list), availability
    """
    data = {"product_url": url, "title": None, "sku": None, "price": None,
            "description": None, "attributes": {}, "images": [], "availability": None}

    # Title
    title_el = soup.select_one("h1, h1.product-title, .product-title")
    if title_el:
        data["title"] = title_el.get_text(strip=True)

    # Price
    # Look for common price selectors
    price_el = soup.select_one(".price, .product-price, [itemprop=price]")
    if price_el:
        data["price"] = price_el.get_text(strip=True)
    else:
        # fallback search for $ in text blocks
        text = soup.get_text(" ", strip=True)
        m = re.search(r"\$\s*\d[\d,\.]*", text)
        if m:
            data["price"] = m.group(0)

    # SKU or product code
    # Look for labels like 'SKU', 'Product Number', 'Item #'
    text = soup.get_text("\n", strip=True)
    m = re.search(r"(SKU|Item #|Item\s+Number|Product\s+Number)\s*[:#]?\s*([A-Za-z0-9\-]+)", text, re.I)
    if m:
        data["sku"] = m.group(2).strip()

    # Description: look for elements with class or id
    desc_el = soup.select_one(".product-description, #description, .description, [itemprop=description]")
    if desc_el:
        data["description"] = desc_el.get_text(" ", strip=True)
    else:
        # fallback: find a <section> with 'description' in class or id
        for sec in soup.find_all(["section", "div"]):
            attr = " ".join((sec.get("class") or []) + [sec.get("id") or ""])
            if "description" in attr.lower():
                data["description"] = sec.get_text(" ", strip=True)
                break

    # Attributes/specs: look for tables or lists
    attrs = {}
    # table rows
    for table in soup.select("table"):
        for row in table.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                key = th.get_text(" ", strip=True)
                val = td.get_text(" ", strip=True)
                attrs[key] = val
    # key-value lists
    for dl in soup.select("dl"):
        dts = dl.select("dt")
        dds = dl.select("dd")
        for k, v in zip(dts, dds):
            attrs[k.get_text(" ", strip=True)] = v.get_text(" ", strip=True)
    # any element with class 'spec' or 'product-attributes'
    for li in soup.select(".product-attributes li, .specs li, .product-specs li"):
        txt = li.get_text(" ", strip=True)
        if ":" in txt:
            k, v = txt.split(":", 1)
            attrs[k.strip()] = v.strip()
    data["attributes"] = attrs

    # Images: collect image src from <img> tags within product gallery or content
    imgs = []
    # look inside common gallery containers
    for img in soup.select(".product-gallery img, .product-media img, img"):
        src = img.get("data-src") or img.get("src") or img.get("data-zoom")
        if not src:
            continue
        full = urljoin(url, src)
        if full not in imgs:
            imgs.append(full)
    data["images"] = imgs

    # Availability: search for 'In Stock' or 'Out of stock'
    page_text = soup.get_text(" ", strip=True).lower()
    if "out of stock" in page_text or "sold out" in page_text:
        data["availability"] = "out of stock"
    elif "add to cart" in page_text or "in stock" in page_text:
        data["availability"] = "available"
    else:
        data["availability"] = None

    return data

def download_image(url, target_folder):
    os.makedirs(target_folder, exist_ok=True)
    try:
        r = session.get(url, stream=True, timeout=20)
        r.raise_for_status()
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = re.sub(r"\W+", "_", url)[:40] + ".jpg"
        target_path = os.path.join(target_folder, filename)
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(1024*8):
                f.write(chunk)
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        return target_path
    except Exception as e:
        print(f"[WARN] Failed to download image {url}: {e}")
        return None

def main():
    print("Starting scraper for:", BASE_URL)
    allowed = check_robots_allowed(BASE_URL, HEADERS["User-Agent"], path=urlparse(BASE_URL).path)
    if not allowed:
        print("[ABORT] robots.txt disallows scraping this path. Exiting.")
        return

    results = []
    to_visit = [BASE_URL]
    visited_listing_urls = set()
    page_count = 0

    # Crawl listing pages using next links (breadth-first)
    while to_visit:
        listing_url = to_visit.pop(0)
        if listing_url in visited_listing_urls:
            continue
        print(f"[LISTING] Fetching: {listing_url}")
        soup = get_soup(listing_url)
        if not soup:
            break
        page_count += 1
        visited_listing_urls.add(listing_url)

        products, next_page = parse_listing_page(soup, BASE_URL)
        print(f"[FOUND] {len(products)} product links on this page.")
        # For each product link, fetch details
        for p in tqdm(products, desc="Products", unit="prod"):
            prod_url = p["product_url"]
            # fetch product page
            psoup = get_soup(prod_url)
            if not psoup:
                print(f"[WARN] Skipping product (fetch failed): {prod_url}")
                continue
            pdata = parse_product_page(psoup, prod_url)
            # combine listing partial info if present
            if p.get("title") and not pdata.get("title"):
                pdata["title"] = p.get("title")
            if p.get("price") and not pdata.get("price"):
                pdata["price"] = p.get("price")
            # download images
            downloaded = []
            for img in pdata.get("images", []):
                local = download_image(img, IMAGES_DIR)
                if local:
                    downloaded.append(local)
            pdata["downloaded_images"] = downloaded
            results.append(pdata)

        # pagination
        if next_page:
            print("[PAGINATION] Next page:", next_page)
            if next_page not in visited_listing_urls:
                to_visit.append(next_page)
        else:
            print("[PAGINATION] No next page detected.")
        if MAX_PAGES and page_count >= MAX_PAGES:
            print(f"[LIMIT] Reached MAX_PAGES = {MAX_PAGES}")
            break

    # Save results
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[DONE] Saved {len(results)} products to {OUTPUT_JSON}")
    print(f"[IMAGES] Images saved to ./{IMAGES_DIR}/ (if download succeeded)")

if __name__ == "__main__":
    main()
