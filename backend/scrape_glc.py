import asyncio
import dotenv

dotenv.load_dotenv(".env")
from functii import search_cars
from car_database import car_db_optimizer


async def run():
    ads = await search_cars(
        make="Mercedes",
        model="GLC",
        site="both",
        limit=2000,
        max_pages=15,
        max_price=1000000,
    )
    for ad in ads:
        import re

        raw_price = str(ad.get("price", "0"))
        p_clean = re.sub("\\D", "", raw_price)
        ad["price"] = int(p_clean) if p_clean else 0
    car_db_optimizer.upsert_ads(ads)
    print("Inserted", len(ads))


asyncio.run(run())
