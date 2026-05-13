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

# 1. Modelele prioritare pentru a menține platforma proaspătă
TOP_MODELS = [
    ("bmw", "seria-3"),
    ("bmw", "seria-5"),
    ("audi", "a4"),
    ("volkswagen", "golf"),
    ("volkswagen", "passat"),
    ("skoda", "octavia"),
    ("mercedes", "c-class")
]

async def scrape_and_save(make, model):
    print(f"[{time.strftime('%X')}] Extrag oferte pentru {make.upper()} {model.upper()}...")
    try:
        # Caută cele mai recente oferte (max_pages=5 înseamnă că extrage destul de multe)
        results = await search_cars(
            make=make,
            model=model,
            max_price=999999, # Argument obligatoriu cerut de functii.py
            site='both',
            limit=300,
            max_pages=10,
            sort='newest' # Vrem cele mai NOI anunțuri adăugate, indiferent de preț/an
        )
        
        saved_count = 0
        for car in results:
            try:
                # Trebuie să adăugăm marca și modelul în dicționar, 
                # deoarece scraperul nu le returnează by default.
                car['make'] = make
                car['model'] = model
                
                # Curățăm datele pentru PostgreSQL (care este strict typed, nu acceptă stringuri în loc de Integer)
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
                    price_raw = re.sub(r'\D', '', str(car['price']))
                    car['price'] = int(price_raw) if price_raw else 0
                
                # `upsert_ad` va insera masina DACA NU EXISTA, si ii va face UPDATE la `price` si `last_seen` DACA EXISTA
                car_db_optimizer.upsert_ad(car)
                saved_count += 1
            except Exception as db_err:
                print(f" Eroare DB pt masina {car.get('link')[:30]}: {db_err}")
                
        print(f"[{time.strftime('%X')}] Succes! Am actualizat {saved_count} mașini în Supabase.")
    except Exception as e:
        print(f"[{time.strftime('%X')}] Eroare la scraping pt {make} {model}: {e}")

async def main():
    print("=======================================")
    print(" CAR SNIPER - GLOBAL CRAWLER INITIATED ")
    print("=======================================")
    print("Apasă CTRL+C pentru a opri scriptul.\n")
    
    while True:
        print(f"--- Începere Ciclu Nou de Scraping: {time.strftime('%X')} ---")
        
        # 1. Scraping pentru fiecare model din lista
        for make, model in TOP_MODELS:
            await scrape_and_save(make, model)
            # Așteptăm 10 secunde între modele ca să nu dăm prea multe requesturi simultan (Rate Limit)
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
