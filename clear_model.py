import os, sys
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

sys.path.insert(0, 'backend')
from car_database import car_db_optimizer

# Clear local SQLite if present
if os.path.exists('database/db.sqlite'):
    import sqlite3
    c = sqlite3.connect('database/db.sqlite')
    c.execute("DELETE FROM ads"); c.commit(); c.close()
    print("SQLite cleared")

# Clear PostgreSQL
with car_db_optimizer.get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM ads")
    row = cur.fetchone()
    total = row["cnt"] if row else 0
    cur.execute("DELETE FROM ads")
    conn.commit()
    print(f"Cleared {total} PostgreSQL ads — live scraping now active")
