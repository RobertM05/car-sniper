import asyncio
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu pentru a avea acces la DATABASE_URL
load_dotenv()

from scraper.autovit_scraper import scrape_autovit
from scraper.olx_scraper import scrape_olx
from car_database import car_db_optimizer

# Brand tiers based on Romanian market volume (ads on OLX + Autovit)
BRAND_TIERS = {
    # Tier 1 — 15,000–30,000 ads: needs 400+ pages to cover fully
    "tier1": {
        "pages": 500,
        "brands": ["Volkswagen", "BMW", "Audi", "Mercedes-Benz"]
    },
    # Tier 2 — 5,000–15,000 ads: 250 pages
    "tier2": {
        "pages": 250,
        "brands": ["Skoda", "Ford", "Renault", "Opel", "Dacia", "Toyota", "Hyundai"]
    },
    # Tier 3 — 2,000–5,000 ads: 100 pages
    "tier3": {
        "pages": 100,
        "brands": ["Peugeot", "Volvo", "Kia", "Seat", "Nissan", "Mazda", "Honda",
                    "Suzuki", "Fiat", "Mini", "Land Rover", "Citroen"]
    },
    # Tier 4 — <2,000 ads: 50 pages is more than enough
    "tier4": {
        "pages": 50,
        "brands": ["Porsche", "Jeep", "Alfa Romeo", "Lexus", "Jaguar", "Chevrolet",
                    "Subaru", "Mitsubishi", "Smart", "Dodge", "Chrysler",
                    "Maserati", "Bentley", "Tesla", "Cupra", "DS Automobiles", "Lancia",
                    "SsangYong", "Abarth", "Infiniti", "Saab", "Rover"]
    }
}

# Build flat lookup: brand → max_pages
BRAND_PAGES = {}
for tier in BRAND_TIERS.values():
    for brand in tier["brands"]:
        BRAND_PAGES[brand] = tier["pages"]

async def run_deep_scrape():
    print("==============================================")
    print("🚗 INIȚIERE DEEP SCRAPE (TOATE MĂRCILE) 🚗")
    print(f"Număr mărci: {len(BRAND_PAGES)}")
    print(f"Tier 1 (500p): {BRAND_TIERS['tier1']['brands']}")
    print(f"Tier 2 (250p): {BRAND_TIERS['tier2']['brands']}")
    print(f"Tier 3 (100p): {BRAND_TIERS['tier3']['brands']}")
    print(f"Tier 4 (50p):  {BRAND_TIERS['tier4']['brands']}")
    print("==============================================\n")

    total_ads_inserted = 0

    for brand, max_pages in BRAND_PAGES.items():
        print(f"\n---> Începem procesarea mărcii: {brand.upper()} (max {max_pages} pagini) <---")
        
        # 1. Scrape Autovit
        try:
            print(f"Scraping Autovit pentru {brand}...")
            autovit_results = await scrape_autovit(make=brand, model="", limit=max_pages * 40, max_pages=max_pages)
            
            if autovit_results:
                inserted_ids = car_db_optimizer.upsert_ads(autovit_results)
                print(f"✅ Autovit: Găsite {len(autovit_results)} | Inserate/Updatate: {len(inserted_ids)}")
                total_ads_inserted += len(inserted_ids)
            else:
                print("❌ Autovit: 0 rezultate găsite.")
        except Exception as e:
            print(f"Eroare Autovit {brand}: {e}")

        # Pauză între site-uri pentru a evita IP ban-ul
        await asyncio.sleep(2)

        # 2. Scrape OLX
        try:
            print(f"Scraping OLX pentru {brand}...")
            olx_results = await scrape_olx(query=brand, limit=max_pages * 40, max_pages=max_pages)
            
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
