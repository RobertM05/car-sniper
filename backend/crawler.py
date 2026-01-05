import asyncio
import logging
from functii import search_cars
from car_database import car_db_optimizer
import random

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define Targets (Eventually load from DB or config)
TARGETS = [
    {"make": "BMW", "model": "X6"},
    {"make": "BMW", "model": "Seria 3"},
    {"make": "BMW", "model": "Seria 5"},
    {"make": "Audi", "model": "A4"},
    {"make": "Audi", "model": "Q7"},
    {"make": "Audi", "model": "Q8"},
    {"make": "Mercedes", "model": "Clasa E"},
    {"make": "Volkswagen", "model": "Golf"},
]

async def crawl_target(target):
    make = target["make"]
    model = target["model"]
    
    logging.info(f"🕷️  Crawling {make} {model} (using Unified Scraper Logic)...")
    
    try:
        # Use the EXACT same logic as the "Live Scraper" via search_cars
        # We pass a very high max_price to get everything
        results = await search_cars(
            make=make,
            model=model,
            max_price=10000000, # Effectively no limit
            site="both",
            limit=1000, # Fetch deep
            max_pages=20  # Go deep
        )
        
        count = 0
        for ad in results:
            # search_cars returns cleaned, normalized data
            # Format it for the DB
            try:
                # Safe price parsing (search_cars returns int for 'price' usually, or string)
                price_val = 0
                raw_price = str(ad.get("price", "0"))
                # If it contains "EUR", strip it. Ideally search_cars returns int.
                # Let's handle both.
                if isinstance(ad.get("price"), int):
                    price_val = ad.get("price")
                else: 
                     # fallback
                     import re
                     p_clean = re.sub(r"\D", "", raw_price)
                     price_val = int(p_clean) if p_clean else 0

                # Emergency Repair Logic
                is_luxury = any(x in model.lower() for x in ["x6", "x7", "q8", "q7", "gle", "gls", "g-class"])
                
                # 1. Price Check: Luxury cars < 15k are flagged logic
                is_suspicious_price = is_luxury and (0 < price_val < 15000)
                
                # 2. Image Check
                is_missing_image = not ad.get("image") or "no_thumbnail" in str(ad.get("image"))

                # Trigger repair only if image is missing to optimize performance.
                # If image is missing, we also validate price.
                if is_missing_image:
                     logging.info(f"🔧 Attempting repair for: {ad.get('title')} (Price: {price_val})")
                     try:
                         import aiohttp
                         from bs4 import BeautifulSoup
                         import json as _json_fix
                         
                         async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                             async with sess.get(ad.get("link"), timeout=10) as r:
                                 # GHOST AD CHECK
                                 # If 404 or redirected to homepage (autovit.ro / olx.ro main page), the ad is GONE.
                                 if r.status == 404 or len(str(r.url)) < 30: # Simple heuristic for homepage redirect
                                     logging.info(f"🗑️ Found GHOST AD (404/Redirect): {ad.get('title')}. Deleting...")
                                     car_db_optimizer.delete_ad(ad.get("id"))
                                     continue # Skip Upsert
                                     
                                 if r.status == 200:
                                     html = await r.text()
                                     soup = BeautifulSoup(html, "html.parser")
                                     
                                     # ALWAYS Try to Fix Price (if we are here)
                                     # Try 1: Next Data
                                     nd = soup.find("script", {"id": "__NEXT_DATA__"})
                                     if nd and nd.string:
                                         d = _json_fix.loads(nd.string)
                                         pp = d.get("props", {}).get("pageProps", {})
                                         adv = pp.get("advert") or pp.get("data", {}).get("advert")
                                         if adv:
                                             p = adv.get("price", {}).get("value")
                                             if p:
                                                 new_p = int(p)
                                                 # Update if new price is better/different and looks valid
                                                 # For suspicious ones, we take the new price.
                                                 # For others, we assume deep fetch is more accurate.
                                                 if new_p > price_val: 
                                                     price_val = new_p
                                                     logging.info(f"    ✅ Fixed Price: {price_val}")
                                     
                                     # ALWAYS Try to Fix Image (if we are here)
                                     if is_missing_image:
                                         og = soup.find("meta", attrs={"property": "og:image"})
                                         if og and og.get("content"):
                                             ad["image"] = og.get("content")
                                             logging.info(f"    ✅ Fixed Image")
                                         elif not ad.get("image"):
                                             # Try finding gallery image
                                             gal = soup.find("img", {"class": "css-1bmvjcs"}) # Common OLX/Autovit class
                                             if gal:
                                                  ad["image"] = gal.get("src")
                     except Exception as e:
                         logging.warning(f"    ❌ Repair failed: {e}")

                db_ad = {
                    "source": ad.get("subsource") or ad.get("source", "Unknown"),
                    "make": make,
                    "model": model,
                    "title": ad.get("title"),
                    "link": ad.get("link"),
                    "image": ad.get("image"),
                    "price": price_val,
                    "year": ad.get("year"),
                    "km": ad.get("km"),
                    "id": ad.get("id") 
                }
                
                car_db_optimizer.upsert_ad(db_ad)
                count += 1
            except Exception as e:
                logging.warning(f"Failed to upsert ad: {e}")
                
        logging.info(f"✅ Finished {make} {model}: Saved {count} ads.")
        
    except Exception as e:
        logging.error(f"Error crawling {make} {model}: {e}")

async def run_crawler():
    logging.info("🚀 Starting Search Engine Crawler (Unified Mode)...")
    
    # Initial DB Init
    car_db_optimizer.init_database()
    
    while True:
        logging.info("♻️  Starting cycle...")
        
        for target in TARGETS:
            await crawl_target(target)
            # Sleep between requests to be polite
            await asyncio.sleep(random.randint(5, 10))
            
        # Clean up stale ads
        cleaned = car_db_optimizer.deactivate_stale_ads(hours_threshold=24)
        if cleaned > 0:
            logging.info(f"🧹 Deactivated {cleaned} stale ads.")
            
        logging.info("💤 Cycle done. Sleeping for 10 minutes...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(run_crawler())
