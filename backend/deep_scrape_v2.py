"""
Deep Scrape v2 — Model-level scraping with year sharding.

Uses the same smart logic as live scraping (category URLs, proper slugs,
model validation) but iterates over ALL models from the catalog.

When a model has too many ads (near the ~100-page pagination cap),
auto-shards by year ranges to ensure complete coverage.
"""

import asyncio
import json
import os
import random
import sys
import time
from dotenv import load_dotenv

# Must load .env BEFORE importing car_database (which connects to DB at import time)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))
from functii import search_cars
from car_database import car_db_optimizer

OVERFLOW_THRESHOLD = 800
YEAR_SHARD_SIZE = 5
MIN_YEAR = 1950
MAX_YEAR = 2026

# Rate limiting — prevents IP bans
MODEL_DELAY_MIN = 8
MODEL_DELAY_MAX = 15
BRAND_DELAY_MIN = 20
BRAND_DELAY_MAX = 35
COOLDOWN_EVERY_N = 20
COOLDOWN_SECONDS = 120


def load_catalog():
    with open(os.path.join(os.path.dirname(__file__), "autovit_catalog.json")) as f:
        return json.load(f)


async def scrape_model(make, model):
    """Scrape a single model. Auto-shard by year if it overflows."""
    print(f"  {make} {model}...", end=" ", flush=True)

    try:
        results = await search_cars(
            make=make,
            model=model,
            site="both",
            limit=20000,
            max_pages=1000,
            min_year=MIN_YEAR,
            max_year=MAX_YEAR,
            sort="newest",
            require_photos=False,
        )
    except Exception as e:
        print(f"error: {e}")
        return []

    if len(results) < OVERFLOW_THRESHOLD:
        print(f"{len(results)} ads")
        return results

    # Overflow — shard by year
    print(f"{len(results)} (overflow, sharding by year...)")
    seen = {r.get("link", "") for r in results}
    all_results = list(results)

    for ys in range(MIN_YEAR, MAX_YEAR, YEAR_SHARD_SIZE):
        ye = min(ys + YEAR_SHARD_SIZE - 1, MAX_YEAR)
        try:
            shard = await search_cars(
                make=make,
                model=model,
                site="both",
                limit=20000,
                max_pages=1000,
                min_year=ys,
                max_year=ye,
                sort="newest",
                require_photos=False,
            )
        except Exception:
            continue
        for ad in shard:
            link = ad.get("link", "")
            if link and link not in seen:
                seen.add(link)
                all_results.append(ad)
        await asyncio.sleep(1)

    print(f"    -> {len(all_results)} total after sharding")
    return all_results


async def main():
    catalog = load_catalog()
    total_models = sum(len(m) for m in catalog.values())
    print(f"Deep Scrape v2: {len(catalog)} brands, {total_models} models\n")

    total_inserted = 0
    model_count = 0
    start_time = time.time()

    for brand, models in catalog.items():
        print(f"\n-- {brand.upper()} ({len(models)} models) --")
        for model in models:
            model_count += 1
            results = await scrape_model(brand, model)
            if results:
                try:
                    ids = car_db_optimizer.upsert_ads(results)
                    inserted = len(ids)
                    total_inserted += inserted
                    print(f"    upserted {inserted}")
                except Exception as e:
                    print(f"    DB error: {e}")

            # Rate limiting
            delay = random.uniform(MODEL_DELAY_MIN, MODEL_DELAY_MAX)
            if model_count % COOLDOWN_EVERY_N == 0:
                elapsed = time.time() - start_time
                print(
                    f"    ⏸  Cooldown ({COOLDOWN_SECONDS}s) — {model_count} models done, {elapsed:.0f}s elapsed"
                )
                await asyncio.sleep(COOLDOWN_SECONDS)
            else:
                await asyncio.sleep(delay)

        # Longer pause between brands
        brand_delay = random.uniform(BRAND_DELAY_MIN, BRAND_DELAY_MAX)
        print(f"  ⏸  Brand pause {brand_delay:.0f}s...")
        await asyncio.sleep(brand_delay)

    print(f"\nDONE. {total_inserted} total ads upserted.")


if __name__ == "__main__":
    asyncio.run(main())
