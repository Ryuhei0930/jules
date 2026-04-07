import sqlite3
import datetime
import hashlib
import os

DB_FILE = 'staging_app.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            monthly_limit INTEGER DEFAULT 50
        )
    ''')
    # Settings table (for API Key)
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Generations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
        c.execute("INSERT INTO users (username, password, role, monthly_limit) VALUES (?, ?, 'admin', 99999)",
                  ('admin', hash_password(admin_pass)))

    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return {"id": user[0], "role": user[1]} if user else None

def get_users():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, role, monthly_limit FROM users WHERE role = 'client'")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users

def add_user(username, password, monthly_limit):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, monthly_limit) VALUES (?, ?, 'client', ?)",
                  (username, hash_password(password), monthly_limit))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def update_user_limit(user_id, monthly_limit):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET monthly_limit = ? WHERE id = ?", (monthly_limit, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_api_key():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'api_key'")
    result = c.fetchone()
    conn.close()
    return result[0] if result else ""

def set_api_key(api_key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('api_key', ?)", (api_key,))
    conn.commit()
    conn.close()

def get_base_prompt():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'base_prompt'")
    result = c.fetchone()
    conn.close()
    default_prompt = "この空の部屋の写真に自然に家具を配置してください。元のパースペクティブと照明を維持すること。"
    return result[0] if result else default_prompt

def set_base_prompt(prompt):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('base_prompt', ?)", (prompt,))
    conn.commit()
    conn.close()

def log_generation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure timezone consistency by using python's utcnow
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO generations (user_id, timestamp) VALUES (?, ?)', (user_id, now))
    conn.commit()
    conn.close()

def get_user_monthly_usage(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    current_month = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m')
    c.execute("SELECT COUNT(*) FROM generations WHERE user_id = ? AND timestamp LIKE ?", (user_id, f"{current_month}%"))
    count = c.fetchone()[0]

    c.execute("SELECT monthly_limit FROM users WHERE id = ?", (user_id,))
    limit_result = c.fetchone()
    limit = limit_result[0] if limit_result else 0

    conn.close()
    return count, limit

def get_all_monthly_usage():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    current_month = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m')

    c.execute('''
        SELECT u.username, u.monthly_limit, COUNT(g.id) as count
        FROM users u
        LEFT JOIN generations g ON u.id = g.user_id AND g.timestamp LIKE ?
        WHERE u.role = 'client'
        GROUP BY u.id
    ''', (f"{current_month}%",))

    usage = [dict(row) for row in c.fetchall()]
    conn.close()
    return usage

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
