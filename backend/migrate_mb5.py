import os
import psycopg2


def migrate():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set. Skipping Postgres migration.")
        return

    print("Connecting to DB for migration...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()

    print("Adding ON DELETE CASCADE to alerts.user_email...")
    try:
        cursor.execute(
            "ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_user_email_fkey;"
        )
        cursor.execute(
            "ALTER TABLE alerts ADD CONSTRAINT alerts_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE;"
        )
        print("Constraint added successfully.")
    except Exception as e:
        print(f"Error adding constraint: {e}")

    print("Creating index on alerts(make, model)...")
    try:
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alerts_make_model ON alerts(make, model);"
        )
        print("Index idx_alerts_make_model created.")
    except Exception as e:
        print(f"Error creating index: {e}")

    print("Creating index on search_stats(make, model)...")
    try:
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_search_stats_make_model ON search_stats(make, model);"
        )
        print("Index idx_search_stats_make_model created.")
    except Exception as e:
        print(f"Error creating index: {e}")

    print("Migration MB-5 complete.")
    conn.close()


if __name__ == "__main__":
    migrate()
