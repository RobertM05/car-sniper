import os
import sys
import logging
from datetime import datetime, timedelta

# Add the current directory to sys.path so we can import car_database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from car_database import CarDatabaseOptimizer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    logging.info("Starting automated database pruning...")

    db = CarDatabaseOptimizer()

    # 3 months is roughly 90 days
    cutoff_date = datetime.now() - timedelta(days=90)

    logging.info(
        f"Deleting car records inactive or last seen before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Delete inactive cars older than 90 days or any car not seen in 90 days
            query = """
                DELETE FROM ads 
                WHERE (active = FALSE AND updated_at < %s)
                   OR last_seen < %s
            """

            cursor.execute(query, (cutoff_date, cutoff_date))
            deleted_count = cursor.rowcount
            conn.commit()

            logging.info(f"Successfully pruned {deleted_count} car records.")

    except Exception as e:
        logging.error(f"Error during database pruning: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
