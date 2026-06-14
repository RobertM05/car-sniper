import asyncio, dotenv
dotenv.load_dotenv('.env')
from functii import search_cars
from car_database import car_db_optimizer

async def run():
    ads = await search_cars(make='Mercedes', model='Clasa E', site='both', limit=5000, max_pages=150, max_price=1000000)
    print('Inserted', len(ads))

asyncio.run(run())
