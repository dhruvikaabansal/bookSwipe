import sqlite3
import os

def init_db():
    os.makedirs("db", exist_ok=True)
    db_path = "db/app.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_actions (
        user_id TEXT,
        book_id INTEGER,
        action TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, book_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()
