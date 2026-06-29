import asyncio
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu pentru a avea acces la DATABASE_URL
load_dotenv()

from scraper.autovit_scraper import scrape_autovit
from scraper.olx_scraper import scrape_olx
from car_database import car_db_optimizer

# O listă exhaustivă de mărci auto prezente pe piața din România
ALL_BRANDS = [
    "Volkswagen", "BMW", "Audi", "Mercedes-Benz", "Skoda", "Ford", "Renault",
    "Opel", "Dacia", "Peugeot", "Toyota", "Volvo", "Hyundai", "Kia", "Seat",
    "Nissan", "Mazda", "Honda", "Suzuki", "Fiat", "Mini", "Land Rover",
    "Porsche", "Jeep", "Alfa Romeo", "Lexus", "Jaguar", "Chevrolet",
    "Subaru", "Mitsubishi", "Smart", "Citroen", "Dodge", "Chrysler",
    "Maserati", "Bentley", "Tesla", "Cupra", "DS Automobiles", "Lancia",
    "SsangYong", "Abarth", "Infiniti", "Saab", "Rover"
]

MAX_PAGES_PER_BRAND = 150  # 150 pagini per marcă per site

async def run_deep_scrape():
    print("==============================================")
    print("🚗 INIȚIERE DEEP SCRAPE (TOATE MĂRCILE) 🚗")
    print(f"Număr mărci: {len(ALL_BRANDS)}")
    print(f"Pagini per marcă per site: {MAX_PAGES_PER_BRAND}")
    print("==============================================\n")

    total_ads_inserted = 0

    for brand in ALL_BRANDS:
        print(f"\n---> Începem procesarea mărcii: {brand.upper()} <---")
        
        # 1. Scrape Autovit
        try:
            print(f"Scraping Autovit pentru {brand}...")
            # Preluăm toate anunțurile pentru brand, indiferent de model
            autovit_results = await scrape_autovit(make=brand, model="", limit=MAX_PAGES_PER_BRAND * 40, max_pages=MAX_PAGES_PER_BRAND)
            
            if autovit_results:
                inserted_ids = car_db_optimizer.upsert_ads(autovit_results)
                print(f"✅ Autovit: Găsite {len(autovit_results)} | Inserate/Updatate: {len(inserted_ids)}")
                total_ads_inserted += len(inserted_ids)
            else:
                print("❌ Autovit: 0 rezultate găsite.")
        except Exception as e:
            print(f"Eroare Autovit {brand}: {e}")

        # Pauză mică pentru a evita IP ban-ul
        await asyncio.sleep(2)

        # 2. Scrape OLX
        try:
            print(f"Scraping OLX pentru {brand}...")
            olx_results = await scrape_olx(query=brand, limit=MAX_PAGES_PER_BRAND * 40, max_pages=MAX_PAGES_PER_BRAND)
            
            if olx_results:
                inserted_ids = car_db_optimizer.upsert_ads(olx_results)
                print(f"✅ OLX: Găsite {len(olx_results)} | Inserate/Updatate: {len(inserted_ids)}")
                total_ads_inserted += len(inserted_ids)
            else:
                print("❌ OLX: 0 rezultate găsite.")
        except Exception as e:
            print(f"Eroare OLX {brand}: {e}")

        # Pauză între branduri pentru siguranță
        print(f"Pauză 5 secunde înainte de următorul brand...")
        await asyncio.sleep(5)

    print("\n==============================================")
    print(f"✅ DEEP SCRAPE FINALIZAT CU SUCCES ✅")
    print(f"Număr total de ad-uri procesate și salvate în DB: {total_ads_inserted}")
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(run_deep_scrape())
