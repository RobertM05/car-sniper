import asyncio
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu pentru a avea acces la DATABASE_URL
load_dotenv()

from scraper.autovit_scraper import scrape_autovit
from scraper.olx_scraper import scrape_olx
from car_database import car_db_optimizer
from logger import get_logger
from metrics import metrics
from dead_letter import dead_letter

log = get_logger('deep_scrape')

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
    log.info("Deep scrape starting", extra={"brands": len(ALL_BRANDS), "pages_per_brand": MAX_PAGES_PER_BRAND})

    total_ads_inserted = 0

    for brand in ALL_BRANDS:
        log.info("Processing brand", extra={"brand": brand})
        
        # 1. Scrape Autovit
        try:
            log.info("Scraping Autovit", extra={"brand": brand})
            # Preluăm toate anunțurile pentru brand, indiferent de model
            autovit_results = await scrape_autovit(make=brand, model="", limit=MAX_PAGES_PER_BRAND * 40, max_pages=MAX_PAGES_PER_BRAND)
            
            if autovit_results:
                metrics.increment("ads_scraped", len(autovit_results))
                inserted_ids = car_db_optimizer.upsert_ads(autovit_results)
                metrics.increment("ads_inserted", len(inserted_ids))
                log.info("Autovit results", extra={"brand": brand, "found": len(autovit_results), "inserted": len(inserted_ids)})
                total_ads_inserted += len(inserted_ids)
            else:
                log.warning("Autovit: no results", extra={"brand": brand})
        except Exception as e:
            log.error("Autovit scrape failed", extra={"brand": brand, "error": str(e)})
            metrics.increment("errors")

        # Pauză mică pentru a evita IP ban-ul
        await asyncio.sleep(2)

        # 2. Scrape OLX
        try:
            log.info("Scraping OLX", extra={"brand": brand})
            olx_results = await scrape_olx(query=brand, limit=MAX_PAGES_PER_BRAND * 40, max_pages=MAX_PAGES_PER_BRAND)
            
            if olx_results:
                metrics.increment("ads_scraped", len(olx_results))
                inserted_ids = car_db_optimizer.upsert_ads(olx_results)
                metrics.increment("ads_inserted", len(inserted_ids))
                log.info("OLX results", extra={"brand": brand, "found": len(olx_results), "inserted": len(inserted_ids)})
                total_ads_inserted += len(inserted_ids)
            else:
                log.warning("OLX: no results", extra={"brand": brand})
        except Exception as e:
            log.error("OLX scrape failed", extra={"brand": brand, "error": str(e)})
            metrics.increment("errors")

        # Pauză între branduri pentru siguranță
        await asyncio.sleep(5)

    log.info("Deep scrape complete", extra={"total_inserted": total_ads_inserted})

if __name__ == "__main__":
    asyncio.run(run_deep_scrape())
