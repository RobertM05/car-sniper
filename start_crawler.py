import asyncio
import time
import sys
import os
from dotenv import load_dotenv

# Adaugă folderul backend în calea de căutare pentru ca importul "scraper" din functii.py să funcționeze
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Încărcăm variabilele de mediu (pentru Supabase)
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

from backend.functii import search_cars
from backend.car_database import car_db_optimizer
from backend.logger import get_logger
from backend.metrics import metrics
from backend.dead_letter import dead_letter

log = get_logger('start_crawler')

import json

catalog_path = os.path.join(os.path.dirname(__file__), 'backend', 'autovit_catalog.json')
try:
    with open(catalog_path, 'r') as f:
        BRANDS_AND_MODELS = json.load(f)
    log.info("Loaded catalog", extra={"brands": len(BRANDS_AND_MODELS), "models": sum(len(m) for m in BRANDS_AND_MODELS.values())})
except Exception as e:
    log.warning("Catalog load failed, using fallback", extra={"error": str(e)})
    BRANDS_AND_MODELS = {
        "BMW": ["Seria 1", "Seria 3", "Seria 5", "X3", "X5"],
        "Mercedes-Benz": ["Clasa C", "Clasa E", "Clasa S", "GLC", "GLE"]
    }

@metrics.timed('scrape_and_classify')
async def scrape_and_classify(make, possible_models):
    log.info("Starting brand scrape", extra={"make": make, "models_count": len(possible_models)})
    log.info("Starting brand scrape", extra={"make": make, "models_count": len(possible_models)})
    try:
        is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        
        saved_count = 0
        total_found = 0
        
        for model in possible_models:
            try:
                if is_github_actions:
                    mode = "RAPID" if is_github_actions else "FULL_SYNC"
                    mode = "RAPID" if is_github_actions else "FULL_SYNC"
                # Caută mașini PENTRU UN MODEL SPECIFIC, respectând filtrele site-urilor!
                # MASTER BLUEPRINT: Temporal Search Space Sharding
                async def get_all_cars_sharded(m_make, m_model, min_y=1950, max_y=2026):
                    res = await search_cars(
                        make=m_make,
                        model=m_model,
                        min_year=min_y,
                        max_year=max_y,
                        max_price=999999,
                        site='both',
                        limit=50 if is_github_actions else 25000,
                        max_pages=3 if is_github_actions else 1000,
                        sort='newest'
                    )
                    # If we hit near the 1000-ad pagination wall, split the year range
                    if len(res) >= 800 and not is_github_actions and min_y < max_y:
                        mid_y = (min_y + max_y) // 2
                        log.warning("Sharding triggered", extra={"make": m_make, "model": m_model, "min_y": min_y, "max_y": max_y, "hit_count": len(res)})
                        res1 = await get_all_cars_sharded(m_make, m_model, min_y, mid_y)
                        await asyncio.sleep(1)
                        res2 = await get_all_cars_sharded(m_make, m_model, mid_y + 1, max_y)
                    
                        # Deduplicate combined results by link
                        seen_links = set()
                        combined_res = []
                        for c in res1 + res2:
                            link = c.get('link')
                            if link not in seen_links:
                                seen_links.add(link)
                                combined_res.append(c)
                        return combined_res
                    return res
            
                results = await get_all_cars_sharded(make, model, 1950, 2026)
            
                valid_cars = []
                for car in results:
                    try:
                        # Ne bazăm exact pe filtrul din OLX/Autovit, nu mai ghicim modelul din titlu!
                        car['make'] = make
                        car['model'] = model
                    
                        # Curățăm datele pentru PostgreSQL
                        import re
                        if car.get('year'):
                            try:
                                car['year'] = int(str(car['year']).strip())
                            except:
                                car['year'] = None
                            
                        if car.get('km'):
                            km_raw = re.sub(r'\D', '', str(car['km']))
                            car['km'] = int(km_raw) if km_raw else None
                        
                        if car.get('price'):
                            price_str = str(car['price']).split(',')[0]
                            price_raw = re.sub(r'\D', '', price_str)
                            car['price'] = int(price_raw) if price_raw else 0
                    
                        valid_cars.append(car)
                    except Exception as e:
                        log.error("Car parse error", extra={"link": car.get("link", "")[:60], "error": str(e)})
                    
                if valid_cars:
                    try:
                        car_db_optimizer.upsert_ads(valid_cars)
                        saved_count += len(valid_cars)
                        if not is_github_actions:
                            ghosts = car_db_optimizer.mark_ghost_ads_inactive(make, model, buffer_hours=12)
                            if ghosts > 0:
                                log.info("Ghost ads marked inactive", extra={"make": make, "model": model, "ghosts": ghosts})
                    except Exception as db_err:
                        log.error("DB batch upsert failed", extra={"make": make, "model": model, "error": str(db_err)})
                    for c in valid_cars:
                        try:
                            dead_letter.save(c, error=str(db_err), source="start_crawler")
                        except Exception:
                            pass
            
                total_found += len(results)
                # Sleep scurt între modele pentru a nu fi blocați de Autovit/OLX
                await asyncio.sleep(2)
            except Exception as model_err:
                log.error("Model scrape failed", extra={"make": make, "model": model, "error": str(model_err)})
                import traceback
                traceback.print_exc()
                
        metrics.increment("ads_scraped", total_found)
        metrics.increment("ads_inserted", saved_count)
        log.info("Brand scrape complete", extra={"make": make, "saved": saved_count, "found": total_found})
    except Exception as e:
        log.error("Brand scrape failed", extra={"make": make, "error": str(e)})
        metrics.increment("errors")

async def main():
    log.info("Car Sniper global crawler initiated")
    log.info("Car Sniper global crawler initiated")
    log.info("Car Sniper global crawler initiated")
    
    resume_make = None
    if len(sys.argv) > 1 and sys.argv[1] == '--resume' and len(sys.argv) > 2:
        resume_make = sys.argv[2]
        if resume_make not in BRANDS_AND_MODELS:
            log.warning("Resume brand not found", extra={"brand": resume_make})
            resume_make = None
        else:
            log.info("Resuming from brand", extra={"brand": resume_make})

    while True:
        log.info("Starting new scrape cycle")
        
        if resume_make:
            log.info("Resuming cycle", extra={"brand": resume_make})
        
        # 1. Scraping pentru fiecare marcă în parte (descărcăm sute de mașini și le clasificăm local)
        for make, models in BRANDS_AND_MODELS.items():
            if resume_make and make != resume_make:
                continue
            if resume_make and make == resume_make:
                resume_make = None # Resume matched, continue normally from here
            await scrape_and_classify(make, models)
            # Așteptăm 10 secunde între mărci ca să nu dăm prea multe requesturi simultan
            await asyncio.sleep(10)
            
        # 2. Curățenia generală (The Cleaner)
        # O Rulăm DOAR dacă facem Full Sync (local). Dacă suntem pe Rapid Sync (GitHub), am scanat 
        # doar primele 50 de anunțuri, deci nu putem asuma că restul au dispărut!
        if not os.environ.get("GITHUB_ACTIONS"):
            log.info("Running stale ad cleanup (48h threshold)")
            cleaned = car_db_optimizer.deactivate_stale_ads(hours_threshold=48)
            log.info("Stale ads deactivated", extra={"count": cleaned})
        else:
            log.info("Running stale ad cleanup (48h threshold)")
        
        # 3. Oprește scriptul dacă suntem pe GitHub Actions
        if os.environ.get("GITHUB_ACTIONS"):
            log.info("GitHub Actions detected, stopping after one cycle")
            break
            
        # 4. Pauză până la următorul ciclu (Doar local)
        wait_hours = 4
        log.info("Cycle complete, sleeping", extra={"wait_hours": wait_hours})
        await asyncio.sleep(wait_hours * 3600) 

if __name__ == "__main__":
    asyncio.run(main())
