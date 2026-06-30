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

# Price buckets to bypass ~100 page search caps on both OLX and Autovit
# €500 steps up to €5k, €1k up to €20k, €5k up to €200k
PRICE_BUCKETS = (
    [(i, i + 499) for i in range(0, 5000, 500)] +
    [(i, i + 999) for i in range(5000, 20000, 1000)] +
    [(i, i + 4999) for i in range(20000, 200000, 5000)] +
    [(200000, 999999)]  # catch cars ≥ €200k
)

async def scrape_with_buckets(scraper_fn, brand, site_name, bucket_pause=1.5):
    """Scrape a site across all price buckets, deduplicating by ad ID."""
    all_results = []
    seen_ids = set()
    
    for p_min, p_max in PRICE_BUCKETS:
        print(f"  {site_name} bucket €{p_min}-€{p_max}...", end=" ")
        bucket_results = await scraper_fn(p_min, p_max)
        new_count = 0
        for ad in bucket_results:
            ad_id = ad.get('id') or ad.get('link', '')
            if ad_id not in seen_ids:
                seen_ids.add(ad_id)
                all_results.append(ad)
                new_count += 1
        print(f"{new_count} new, {len(all_results)} total")
        await asyncio.sleep(bucket_pause)
    
    return all_results

async def scrape_buckets(site_name, scraper_fn):
    """Scrape across all price buckets, deduplicating by ad ID."""
    all_results = []
    seen_ids = set()
    for p_min, p_max in PRICE_BUCKETS:
        print(f"  {site_name} €{p_min}-€{p_max}...", end=" ")
        bucket = await scraper_fn(p_min, p_max)
        new = 0
        for ad in bucket:
            aid = ad.get('id') or ad.get('link', '')
            if aid not in seen_ids:
                seen_ids.add(aid)
                all_results.append(ad)
                new += 1
        print(f"{new} new, {len(all_results)} total")
        await asyncio.sleep(1.5)
    return all_results


async def run_deep_scrape():
    print("==============================================")
    print("🚗 INIȚIERE DEEP SCRAPE (TOATE MĂRCILE) 🚗")
    print(f"Număr mărci: {len(BRAND_PAGES)} | Price buckets: {len(PRICE_BUCKETS)}")
    print(f"Tier 1: {BRAND_TIERS['tier1']['brands']}")
    print(f"Tier 2: {BRAND_TIERS['tier2']['brands']}")
    print(f"Tier 3: {BRAND_TIERS['tier3']['brands']}")
    print(f"Tier 4: {BRAND_TIERS['tier4']['brands']}")
    print("==============================================\n")

    total_ads_inserted = 0

    for brand in BRAND_PAGES:
        print(f"\n---> {brand.upper()} <---")
        
        # 1. Autovit — price buckets
        try:
            av_results = await scrape_buckets("Autovit", lambda lo, hi: 
                scrape_autovit(make=brand, model="", limit=4000, max_pages=100,
                               min_price=lo, max_price=hi))
            if av_results:
                ids = car_db_optimizer.upsert_ads(av_results)
                print(f"  ✅ Autovit: {len(av_results)} found | {len(ids)} upserted")
                total_ads_inserted += len(ids)
            else:
                print("  ❌ Autovit: 0")
        except Exception as e:
            print(f"  ❌ Autovit error: {e}")
        await asyncio.sleep(2)

        # 2. OLX — price buckets
        try:
            olx_results = await scrape_buckets("OLX", lambda lo, hi:
                scrape_olx(query=brand, limit=4000, max_pages=100,
                           min_price=lo, max_price=hi, require_photos=False))
            if olx_results:
                ids = car_db_optimizer.upsert_ads(olx_results)
                print(f"  ✅ OLX: {len(olx_results)} found | {len(ids)} upserted")
                total_ads_inserted += len(ids)
            else:
                print("  ❌ OLX: 0")
        except Exception as e:
            print(f"  ❌ OLX error: {e}")
        await asyncio.sleep(5)

    print("\n==============================================")
    print(f"✅ DEEP SCRAPE FINALIZAT — {total_ads_inserted} total")
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(run_deep_scrape())
