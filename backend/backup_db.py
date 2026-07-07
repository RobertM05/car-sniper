import csv
import datetime
import os
from dotenv import load_dotenv
from car_database import car_db_optimizer

load_dotenv()


def export_to_csv():
    print("Începem backup-ul bazei de date...")

    with car_db_optimizer.get_connection() as conn:
        cursor = conn.cursor()

        # Obținem numele coloanelor pentru tabelul ads
        cursor.execute("SELECT * FROM ads LIMIT 0")
        column_names = [desc[0] for desc in cursor.description]

        print(f"Coloanele găsite: {', '.join(column_names)}")

        # Preluăm toate datele
        print("Descărcăm datele de pe Supabase. Te rog așteaptă...")
        cursor.execute("SELECT * FROM ads")
        rows = []
        while True:
            batch = cursor.fetchmany(1000)
            if not batch:
                break
            rows.extend(batch)

        if not rows:
            print("Nu s-au găsit date în tabelul ads.")
            return

        # Generăm numele fișierului bazat pe data și ora curentă
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_ads_{date_str}.csv"

        print(f"Se scriu {len(rows)} rânduri în {filename}...")

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(column_names)  # Header
            writer.writerows(rows)  # Datele

        print("\n✅ BACKUP COMPLET!")
        print(f"Fișierul a fost salvat local ca: {filename}")
        print(
            f"Dimensiune aproximativă: {os.path.getsize(filename) / (1024 * 1024):.2f} MB"
        )


if __name__ == "__main__":
    export_to_csv()
