import asyncio
import time
import sys
import os
import re
from dotenv import load_dotenv

# Adaugă folderul backend în calea de căutare pentru ca importul "scraper" din functii.py să funcționeze
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Încărcăm variabilele de mediu (pentru Supabase)
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

from backend.functii import search_cars
from backend.car_database import car_db_optimizer

# Catalog extins de mașini
BRANDS_AND_MODELS = {
    "BMW": ["Seria 1", "Seria 3", "Seria 4", "Seria 5", "Seria 6", "Seria 7", "Seria 8", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "M3", "M4", "M5", "i3", "i4", "i8"],
    "Audi": ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q5", "Q7", "Q8", "e-tron", "TT"],
    "Volkswagen": ["Golf", "Passat", "Polo", "Tiguan", "Touareg", "Touran", "Jetta", "Arteon", "T-Roc", "T-Cross", "Up!", "Caddy", "Transporter", "ID.3", "ID.4"],
    "Mercedes-Benz": ["Clasa A", "Clasa B", "Clasa C", "Clasa E", "Clasa S", "Clasa V", "GLA", "GLB", "GLC", "GLE", "GLS", "Clasa G", "CLA", "CLS", "Vito", "Sprinter"],
    "Ford": ["Focus", "Fiesta", "Mondeo", "Kuga", "Puma", "Transit", "EcoSport", "Mustang", "Ranger", "S-Max", "C-Max", "Galaxy", "Tourneo"],
    "Dacia": ["Logan", "Sandero", "Duster", "Spring", "Jogger", "Dokker", "Lodgy", "Solenza"],
    "Skoda": ["Octavia", "Superb", "Fabia", "Kodiaq", "Karoq", "Kamiq", "Rapid", "Scala", "Yeti", "Roomster", "Enyaq"],
    "Renault": ["Clio", "Megane", "Captur", "Kadjar", "Laguna", "Zoe", "Talisman", "Koleos", "Twingo", "Kangoo", "Trafic", "Symbol", "Arkana"],
    "Opel": ["Astra", "Corsa", "Insignia", "Mokka", "Crossland", "Grandland", "Zafira", "Meriva", "Vectra", "Vivaro", "Antara"],
    "Toyota": ["Corolla", "Yaris", "RAV4", "Auris", "C-HR", "Camry", "Land Cruiser", "Hilux", "Avensis", "Prius", "Aygo", "Proace"],
    "Peugeot": ["208", "308", "508", "2008", "3008", "5008", "108", "Traveller", "Partner", "Boxer", "Rifter"],
    "Hyundai": ["Tucson", "i20", "i30", "i10", "Kona", "Santa Fe", "Elantra", "Ioniq", "Bayon"],
    "Volvo": ["XC60", "XC90", "XC40", "V90", "V60", "V40", "S90", "S60"],
    "Nissan": ["Qashqai", "Juke", "X-Trail", "Micra", "Navara", "Leaf", "Ariya"],
    "Kia": ["Sportage", "Ceed", "Rio", "Picanto", "Stonic", "Sorento", "Niro", "Optima", "XCeed"],
    "Seat": ["Leon", "Ibiza", "Ateca", "Arona", "Tarraco", "Toledo"],
    "Fiat": ["500", "Tipo", "Panda", "Ducato", "Doblo", "Punto", "Bravo"],
    "Honda": ["Civic", "CR-V", "HR-V", "Jazz", "Accord"],
    "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-30", "CX-3", "Mazda2", "MX-5"],
    "Suzuki": ["Vitara", "Swift", "SX4", "Ignis", "Jimny", "S-Cross", "Swace"],
    "Land Rover": ["Range Rover", "Range Rover Sport", "Range Rover Evoque", "Range Rover Velar", "Discovery", "Defender"],
    "Porsche": ["Cayenne", "Macan", "Panamera", "911", "Taycan"],
    "Jeep": ["Grand Cherokee", "Compass", "Renegade", "Wrangler", "Cherokee"],
    "Mini": ["Cooper", "Countryman", "Clubman"],
    "Alfa Romeo": ["Giulia", "Stelvio", "Giulietta", "159", "Tonale"],
    "Jaguar": ["F-Pace", "XE", "XF", "E-Pace"],
    "Lexus": ["RX", "NX", "UX", "IS", "ES", "CT"],
    "Chevrolet": ["Aveo", "Cruze", "Spark", "Captiva", "Trax", "Camaro", "Corvette"],
    "Mitsubishi": ["Outlander", "ASX", "L200", "Colt", "Pajero", "Eclipse Cross"],
    "Subaru": ["Forester", "Outback", "XV", "Impreza"],
    "Citroen": ["C3", "C4", "C5", "Berlingo", "Jumper", "C1"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
    "Maserati": ["Levante", "Ghibli", "Quattroporte"]
}

async def scrape_by_year(make, possible_models, min_year, max_year):
    print(f"[{time.strftime('%X')}] Căutare pentru {make.upper()} (Anii: {min_year}-{max_year})...")
    try:
        # Căutăm DOAR mașinile din acești ani
        results = await search_cars(
            make=make,
            model="", 
            max_price=999999,
            min_year=min_year,
            max_year=max_year,
            site='both',
            limit=5000, 
            max_pages=30, # Paginația va acoperi lejer mașinile adăugate într-un singur an
            sort='newest'
        )
        
        saved_count = 0
        for car in results:
            try:
                car['make'] = make
                title_lower = str(car.get('title', '')).lower()
                detected_model = None
                
                for m in possible_models:
                    if m.lower() in title_lower:
                        detected_model = m
                        break
                        
                if not detected_model and make.upper() == "BMW":
                    m_bmw = re.search(r'\b([1-8])\d{2}[di]?\b', title_lower)
                    if m_bmw: detected_model = f"Seria {m_bmw.group(1)}"
                if not detected_model and make.upper() == "MERCEDES-BENZ":
                    m_mb = re.search(r'\b([a-z]{1,3})\s?\d{2,3}\b', title_lower)
                    if m_mb: detected_model = m_mb.group(1).upper()

                car['model'] = detected_model
                
                if car.get('year'):
                    try: car['year'] = int(str(car['year']).strip())
                    except: car['year'] = None
                        
                if car.get('km'):
                    km_raw = re.sub(r'\D', '', str(car['km']))
                    car['km'] = int(km_raw) if km_raw else None
                    
                if car.get('price'):
                    price_raw = re.sub(r'\D', '', str(car['price']))
                    car['price'] = int(price_raw) if price_raw else 0
                
                if car['model']:
                    car_db_optimizer.upsert_ad(car)
                    saved_count += 1
            except Exception as db_err:
                pass
                
        print(f"[{time.strftime('%X')}] Succes! Am salvat {saved_count} mașini {make.upper()} ({min_year}-{max_year}).")
    except Exception as e:
        print(f"[{time.strftime('%X')}] Eroare la scraping pt {make} ({min_year}): {e}")

async def main():
    print("=======================================")
    print(" SEEDER INITIATED (HISTORICAL BACKFILL)")
    print("=======================================")
    
    # Generăm o listă de intervale de ani: 1990-1999, 2000-2000, 2001-2001... 2024-2024
    year_ranges = [(1990, 1999)] + [(y, y) for y in range(2000, 2025)]
    
    for make, models in BRANDS_AND_MODELS.items():
        print(f"\n--- Începem preluarea istorică pentru {make.upper()} ---")
        
        for min_y, max_y in year_ranges:
            await scrape_by_year(make, models, min_y, max_y)
            # Așteptăm 3 secunde între ani pentru a nu bloca serverele (Rate Limit)
            await asyncio.sleep(3)
            
        print(f"+++ Am finalizat istoricul pentru {make.upper()}! +++")
        await asyncio.sleep(10)
        
    print("\n[!] TOATĂ POPULAREA S-A TERMINAT CU SUCCES! Baza ta de date este acum gigantică.")

if __name__ == "__main__":
    asyncio.run(main())
