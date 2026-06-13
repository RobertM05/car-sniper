import psycopg2
import os

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'robert.musoiu05@gmail.com'")
    conn.commit()
    print(f"Updated {cursor.rowcount} row(s).")
    cursor.execute("SELECT email, role FROM users WHERE email = 'robert.musoiu05@gmail.com'")
    print(cursor.fetchone())
except Exception as e:
    print("Error:", e)
