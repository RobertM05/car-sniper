import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

from backend.car_database import car_db_optimizer

def main():
    print("Curatam baza de date de masinile cu model gresit...")
    # Executăm un DELETE simplu pentru a goli masinile curente, ca noul crawler sa populeze corect
    with car_db_optimizer.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ads")
        conn.commit()
    print("Baza de date a fost golită. Rulează crawler-ul pentru a obține noile date corecte!")

if __name__ == "__main__":
    main()
