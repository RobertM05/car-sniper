import asyncio
import logging
import random
import dotenv
dotenv.load_dotenv()
from functii import search_cars, infer_car_details
from car_database import car_db_optimizer
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TARGETS = [
    {'make': 'BMW', 'model': 'Seria 1'}, {'make': 'BMW', 'model': 'Seria 3'},
    {'make': 'BMW', 'model': 'Seria 4'}, {'make': 'BMW', 'model': 'Seria 5'},
    {'make': 'BMW', 'model': 'X3'}, {'make': 'BMW', 'model': 'X5'}, {'make': 'BMW', 'model': 'X6'},
    {'make': 'Audi', 'model': 'A3'}, {'make': 'Audi', 'model': 'A4'},
    {'make': 'Audi', 'model': 'A5'}, {'make': 'Audi', 'model': 'A6'},
    {'make': 'Audi', 'model': 'Q3'}, {'make': 'Audi', 'model': 'Q5'},
    {'make': 'Audi', 'model': 'Q7'}, {'make': 'Audi', 'model': 'Q8'},
    {'make': 'Mercedes', 'model': 'Clasa A'}, {'make': 'Mercedes', 'model': 'Clasa C'},
    {'make': 'Mercedes', 'model': 'Clasa E'}, {'make': 'Mercedes', 'model': 'GLC'},
    {'make': 'Mercedes', 'model': 'GLE'},
    {'make': 'Volkswagen', 'model': 'Golf'}, {'make': 'Volkswagen', 'model': 'Passat'},
    {'make': 'Volkswagen', 'model': 'Polo'}, {'make': 'Volkswagen', 'model': 'Tiguan'},
]

async def crawl_target(target):
    make = target['make']
    model = target['model']
    logging.info(f'Crawling {make} {model} (using Unified Scraper Logic)...')
    try:
        results = await search_cars(make=make, model=model, max_price=10000000, site='both', limit=15000, max_pages=500)
        count = 0
        valid_db_ads = []
        for ad in results:
            try:
                price_val = 0
                raw_price = str(ad.get('price', '0'))
                if isinstance(ad.get('price'), int):
                    price_val = ad.get('price')
                else:
                    import re
                    p_clean = re.sub('\\D', '', raw_price)
                    price_val = int(p_clean) if p_clean else 0
                is_luxury = any((x in model.lower() for x in ['x6', 'x7', 'q8', 'q7', 'gle', 'gls', 'g-class']))
                is_suspicious_price = is_luxury and 0 < price_val < 15000
                is_missing_image = not ad.get('image') or 'no_thumbnail' in str(ad.get('image'))
                if is_missing_image:
                    logging.info(f"🔧 Attempting repair for: {ad.get('title')} (Price: {price_val})")
                    try:
                        import aiohttp
                        from bs4 import BeautifulSoup
                        import json as _json_fix
                        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as sess:
                            async with sess.get(ad.get('link'), timeout=10) as r:
                                if r.status == 404 or len(str(r.url)) < 30:
                                    logging.info(f"🗑 Found GHOST AD (404/Redirect): {ad.get('title')}. Deleting...")
                                    car_db_optimizer.delete_ad(ad.get('id'))
                                    continue
                                if r.status == 200:
                                    html = await r.text()
                                    soup = BeautifulSoup(html, 'html.parser')
                                    nd = soup.find('script', {'id': '__NEXT_DATA__'})
                                    if nd and nd.string:
                                        d = _json_fix.loads(nd.string)
                                        pp = d.get('props', {}).get('pageProps', {})
                                        adv = pp.get('advert') or pp.get('data', {}).get('advert')
                                        if adv:
                                            p = adv.get('price', {}).get('value')
                                            if p:
                                                new_p = int(p)
                                                if new_p > price_val:
                                                    price_val = new_p
                                                    logging.info(f'    Fixed Price: {price_val}')
                                    if is_missing_image:
                                        og = soup.find('meta', attrs={'property': 'og:image'})
                                        if og and og.get('content'):
                                            ad['image'] = og.get('content')
                                            logging.info(f'    Fixed Image')
                                        elif not ad.get('image'):
                                            gal = soup.find('img', {'class': 'css-1bmvjcs'})
                                            if gal:
                                                ad['image'] = gal.get('src')
                    except Exception as e:
                        logging.warning(f'     Repair failed: {e}')
                fuel = ad.get('fuel')
                transmission = ad.get('transmission')
                
                # Infer missing data
                if not fuel or not transmission:
                    inf_fuel, inf_trans = infer_car_details(ad.get('title'), make)
                    if not fuel: fuel = inf_fuel
                    if not transmission: transmission = inf_trans
                    
                db_ad = {'source': ad.get('subsource') or ad.get('source', 'Unknown'), 'make': make, 'model': model, 'title': ad.get('title'), 'link': ad.get('link'), 'image': ad.get('image'), 'price': price_val, 'year': ad.get('year'), 'km': ad.get('km'), 'id': ad.get('id'), 'fuel': fuel, 'transmission': transmission}
                valid_db_ads.append(db_ad)
            except Exception as e:
                logging.warning(f'Failed to process ad: {e}')
                
        if valid_db_ads:
            try:
                car_db_optimizer.upsert_ads(valid_db_ads)
                count = len(valid_db_ads)
            except Exception as e:
                logging.warning(f'Failed to batch upsert ads: {e}')

        logging.info(f'Finished {make} {model}: Saved {count} ads.')
    except Exception as e:
        logging.error(f'Error crawling {make} {model}: {e}')

async def run_crawler():
    logging.info(' Starting Search Engine Crawler (Unified Mode)...')
    car_db_optimizer.init_database()
    while True:
        logging.info('♻  Starting cycle...')
        for target in TARGETS:
            await crawl_target(target)
            await asyncio.sleep(random.randint(5, 10))
        try:
            cleaned = car_db_optimizer.deactivate_stale_ads(hours_threshold=168)
            logging.info(f"🧹 Cleaned up {cleaned} stale ads from database.")
        except Exception as e:
            logging.error(f"Error during stale ads cleanup: {e}")
        logging.info('💤 Cycle done. Sleeping for 10 minutes...')
        await asyncio.sleep(600)
if __name__ == '__main__':
    asyncio.run(run_crawler())