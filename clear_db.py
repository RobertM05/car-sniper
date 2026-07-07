import os, sys
from dotenv import load_dotenv
load_dotenv(dotenv_path='backend/.env')
sys.path.insert(0, 'backend')
from car_database import car_db_optimizer

with car_db_optimizer.get_connection() as c:
    cur = c.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM ads")
    total = cur.fetchone()["cnt"]
    cur.execute("DELETE FROM ads")
    c.commit()
    print(f"Cleared {total} ads. Run ./start.sh and search.")
