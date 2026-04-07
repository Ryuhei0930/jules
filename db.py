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
            monthly_limit INTEGER DEFAULT 50,
            mansion_name TEXT
        )
    ''')

    # Apply migration if column doesn't exist (for existing databases)
    try:
        c.execute("ALTER TABLE users ADD COLUMN mansion_name TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
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
            prompt TEXT,
            original_image_path TEXT,
            generated_image_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Apply migration for new columns to generations if they don't exist
    try:
        c.execute("ALTER TABLE generations ADD COLUMN prompt TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE generations ADD COLUMN original_image_path TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE generations ADD COLUMN generated_image_path TEXT")
    except sqlite3.OperationalError:
        pass

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
    c.execute("SELECT id, role, mansion_name FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return {"id": user[0], "role": user[1], "mansion_name": user[2]} if user else None

def get_users():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, role, monthly_limit, mansion_name FROM users WHERE role = 'client'")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users

def add_user(username, password, monthly_limit, mansion_name=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, monthly_limit, mansion_name) VALUES (?, ?, 'client', ?, ?)",
                  (username, hash_password(password), monthly_limit, mansion_name))
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

def log_generation(user_id, prompt=None, original_image_path=None, generated_image_path=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure timezone consistency by using python's utcnow
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO generations (user_id, timestamp, prompt, original_image_path, generated_image_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, now, prompt, original_image_path, generated_image_path))
    conn.commit()
    conn.close()

def get_recent_generations(limit=50):
    """Fetch recent generation logs including prompts and image paths for reporting."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT g.id, g.timestamp, g.prompt, g.original_image_path, g.generated_image_path,
               u.username, u.mansion_name
        FROM generations g
        JOIN users u ON g.user_id = u.id
        ORDER BY g.timestamp DESC
        LIMIT ?
    ''', (limit,))
    logs = [dict(row) for row in c.fetchall()]
    conn.close()
    return logs

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

    # Also fetch the mansion_name from the users table
    c.execute('''
        SELECT u.username, u.mansion_name, u.monthly_limit, COUNT(g.id) as count
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
