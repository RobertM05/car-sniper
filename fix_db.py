import psycopg2
import os

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user'")
    cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'robert.musoiu05@gmail.com'")
    conn.commit()
    print("Database fixed successfully.")
except Exception as e:
    print("Error:", e)
