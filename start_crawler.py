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

import json

catalog_path = os.path.join(os.path.dirname(__file__), 'backend', 'autovit_catalog.json')
try:
    with open(catalog_path, 'r') as f:
        BRANDS_AND_MODELS = json.load(f)
    print(f"Loaded {sum(len(m) for m in BRANDS_AND_MODELS.values())} models across {len(BRANDS_AND_MODELS)} brands from catalog.")
except Exception as e:
    print(f"Eroare la incarcarea catalogului, se foloseste fallback. {e}")
    BRANDS_AND_MODELS = {
        "BMW": ["Seria 1", "Seria 3", "Seria 5", "X3", "X5"],
        "Mercedes-Benz": ["Clasa C", "Clasa E", "Clasa S", "GLC", "GLE"]
    }

async def scrape_and_classify(make, possible_models):
    print(f"[{time.strftime('%X')}] ----------------------------------------------------")
    print(f"[{time.strftime('%X')}] Căutare Detaliată pentru Marca: {make.upper()}...")
    try:
        is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        
        saved_count = 0
        total_found = 0
        
        for model in possible_models:
            if is_github_actions:
                print(f"[{time.strftime('%X')}] Se caută exact modelul: {make} {model} (MOD UPDATER RAPID)")
            else:
                print(f"[{time.strftime('%X')}] Se caută exact modelul: {make} {model} (MOD FULL SYNC)")
                
            # Caută mașini PENTRU UN MODEL SPECIFIC, respectând filtrele site-urilor!
            results = await search_cars(
                make=make,
                model=model, 
                max_price=999999,
                site='both',
                limit=50 if is_github_actions else 5000,
                max_pages=3 if is_github_actions else 150,
                sort='newest'
            )
            
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
                    print(f" Eroare parsare masina {car.get('link')[:30]}: {e}")
                    
            if valid_cars:
                try:
                    car_db_optimizer.upsert_ads(valid_cars)
                    saved_count += len(valid_cars)
                except Exception as db_err:
                    print(f" Eroare DB batch upsert: {db_err}")
            
            total_found += len(results)
            # Sleep scurt între modele pentru a nu fi blocați de Autovit/OLX
            await asyncio.sleep(2)
                
        print(f"[{time.strftime('%X')}] Succes! Am salvat {saved_count} mașini exact filtrate din {total_found} găsite pentru {make.upper()}.")
    except Exception as e:
        print(f"[{time.strftime('%X')}] Eroare la scraping pt {make}: {e}")

async def main():
    print("=======================================")
    print(" CAR SNIPER - GLOBAL CRAWLER INITIATED ")
    print("=======================================")
    print("Apasă CTRL+C pentru a opri scriptul.\n")
    
    while True:
        print(f"--- Începere Ciclu Nou de Scraping: {time.strftime('%X')} ---")
        
        # 1. Scraping pentru fiecare marcă în parte (descărcăm sute de mașini și le clasificăm local)
        for make, models in BRANDS_AND_MODELS.items():
            await scrape_and_classify(make, models)
            # Așteptăm 10 secunde între mărci ca să nu dăm prea multe requesturi simultan
            await asyncio.sleep(10)
            
        # 2. Curățenia generală (The Cleaner)
        print(f"\n--- Rulăm curățenia (Dezactivare anunțuri expirate) ---")
        cleaned = car_db_optimizer.deactivate_stale_ads(hours_threshold=48)
        print(f"Rezultat: Am marcat {cleaned} mașini ca fiind VÂNDUTE/EXPIRATE.\n")
        
        # 3. Oprește scriptul dacă suntem pe GitHub Actions
        if os.environ.get("GITHUB_ACTIONS"):
            print("Execuție pe GitHub Actions detectată. Se încheie procesul fără repaus.")
            break
            
        # 4. Pauză până la următorul ciclu (Doar local)
        wait_hours = 4
        print(f"Ciclu complet finalizat! Așteptăm {wait_hours} ore...")
        await asyncio.sleep(wait_hours * 3600) 

if __name__ == "__main__":
    asyncio.run(main())
