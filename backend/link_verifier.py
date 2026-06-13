import asyncio
import aiohttp
import logging
from car_database import car_db_optimizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_single_link(session, ad):
    try:
        # Some sites block HEAD requests, GET is safer but we close the connection immediately after headers
        async with session.get(ad.get('link'), timeout=8, allow_redirects=True) as response:
            # 404 means the ad is definitely gone
            if response.status == 404:
                return ad, False
                
            if response.status in [403, 429]:
                return ad, True
                
            # If the URL redirects significantly (e.g. back to the homepage or search page)
            # Autovit redirects sold cars to similar cars or homepage.
            # OLX usually keeps the URL but changes content, but sometimes redirects.
            final_url = str(response.url)
            original_url = ad.get('link')
            
            # Very basic redirect check
            if len(final_url) < 35 or ("autovit.ro" in original_url and "autovit.ro/anunt/" not in final_url):
                return ad, False
                
            # For OLX, if it redirects to the homepage
            if "olx.ro" in original_url and final_url == "https://www.olx.ro/":
                return ad, False
                
            return ad, True
    except Exception as e:
        # If it times out or fails, we assume it's still active to avoid false positives
        return ad, True

async def verify_ads_liveness(ads_list):
    """
    Takes a list of ads, pings their links asynchronously.
    If a link is dead, deletes the ad from the database.
    """
    if not ads_list:
        return
        
    logging.info(f"🕵️ Background Verifier: Checking {len(ads_list)} links...")
    
    # To avoid rate limits, don't check more than 50 at a time from search results
    ads_to_check = ads_list[:50]
    
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [check_single_link(session, ad) for ad in ads_to_check if ad.get('link')]
            results = await asyncio.gather(*tasks)
            
            dead_ads = [ad for ad, is_alive in results if not is_alive]
            
            if dead_ads:
                logging.info(f"🗑️ Found {len(dead_ads)} dead links. Deleting from DB...")
                for dead_ad in dead_ads:
                    car_db_optimizer.delete_ad(dead_ad.get('id'))
            else:
                logging.info("✅ All checked links are active.")
                
    except Exception as e:
        logging.error(f"Error in background verifier: {e}")

async def cron_cleanup_ads(limit=100):
    """
    Fetches the oldest active ads and verifies them.
    """
    try:
        with car_db_optimizer.get_connection() as conn:
            cursor = conn.cursor()
            # Fetch ads ordered by last_seen (oldest first)
            cursor.execute('''
                SELECT id, link FROM ads
                WHERE active = TRUE
                ORDER BY last_seen ASC
                LIMIT %s
            ''', (limit,))
            ads_to_check = cursor.fetchall()
            
        if not ads_to_check:
            return 0
            
        logging.info(f"🧹 Cron Cleanup: Checking {len(ads_to_check)} old ads...")
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [check_single_link(session, ad) for ad in ads_to_check if ad.get('link')]
            results = await asyncio.gather(*tasks)
            
            dead_ads = [ad for ad, is_alive in results if not is_alive]
            alive_ads = [ad for ad, is_alive in results if is_alive]
            
            # Delete dead ads
            for dead_ad in dead_ads:
                car_db_optimizer.delete_ad(dead_ad.get('id'))
                
            # Update last_seen for alive ads so they aren't checked again immediately
            if alive_ads:
                alive_ids = tuple([ad.get('id') for ad in alive_ads])
                with car_db_optimizer.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE ads SET last_seen = CURRENT_TIMESTAMP
                        WHERE id IN %s
                    ''', (alive_ids,))
                    conn.commit()
                    
        return len(dead_ads)
    except Exception as e:
        logging.error(f"Error in cron cleanup: {e}")
        return 0
