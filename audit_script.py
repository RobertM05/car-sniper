import json
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.car_database import car_db_optimizer
from backend.functii import search_cars

async def run_audit():
    catalog_path = 'backend/autovit_catalog.json'
    if not os.path.exists(catalog_path):
        print(f"Catalog not found at {catalog_path}")
        return

    with open(catalog_path, 'r') as f:
        catalog = json.load(f)

    # Pick a representative sample
    sample = {
        "BMW": ["Seria 3", "X5"],
        "Audi": ["A4", "Q5"],
        "Mercedes-Benz": ["C-Class", "E-Class"],
        "Volkswagen": ["Golf", "Passat"],
        "Dacia": ["Duster", "Logan"]
    }
    
    results = []
    
    for make, models in sample.items():
        if make not in catalog:
            continue
        for model in models:
            if model not in catalog[make]:
                continue
                
            print(f"Processing {make} {model}...")
            
            # Local DB
            try:
                local_ads = car_db_optimizer.get_active_ads_for_make_model(make, model)
                local_count = len(local_ads)
            except Exception as e:
                print(f"Error querying DB for {make} {model}: {e}")
                local_count = -1
            
            # Scraper
            try:
                scraped_ads = await search_cars(make, model, site='both', limit=10000)
                scraped_count = len(scraped_ads)
            except Exception as e:
                print(f"Error scraping {make} {model}: {e}")
                scraped_count = -1
                
            diff = scraped_count - local_count if scraped_count >= 0 and local_count >= 0 else 0
            pct_diff = 0
            if scraped_count > 0 and local_count >= 0:
                pct_diff = (diff / scraped_count) * 100
                
            results.append({
                "Make": make,
                "Model": model,
                "Local DB Count": local_count,
                "Scraper Count": scraped_count,
                "Difference": diff,
                "% Lost": f"{pct_diff:.2f}%"
            })
            
    print("\n--- RESULTS JSON ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_audit())
