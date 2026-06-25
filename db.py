import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'staging_app.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hash the password."""
    return generate_password_hash(password)

def init_db():
    """Initialize the database schema."""
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mansion_name TEXT NOT NULL,
            monthly_quota INTEGER DEFAULT 50,
            used_quota INTEGER DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    # Create logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            original_image_path TEXT,
            generated_image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Try adding columns if they don't exist (migrations)
    try:
        c.execute('ALTER TABLE users ADD COLUMN mansion_name TEXT NOT NULL DEFAULT ""')
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('ALTER TABLE users ADD COLUMN monthly_quota INTEGER DEFAULT 50')
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('ALTER TABLE users ADD COLUMN used_quota INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    # Insert default admin and test user if empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO users (username, password, mansion_name, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hash_password('admin'), 'Admin Mansion', True))
        c.execute('''
            INSERT INTO users (username, password, mansion_name, monthly_quota)
            VALUES (?, ?, ?, ?)
        ''', ('testuser', hash_password('testpass'), 'Test Mansion', 50))

    conn.commit()
    conn.close()

def get_user(username: str, password: str = None):
    """Get a user by username and optional password check."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user and password:
        if check_password_hash(user['password'], password):
            return user
        else:
            return None

    return user

def increment_quota(user_id: int) -> bool:
    """Increment used quota if under limit."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT used_quota, monthly_quota FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False

    used, quota = row['used_quota'], row['monthly_quota']
    if used >= quota:
        conn.close()
        return False

    c.execute('UPDATE users SET used_quota = used_quota + 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def log_generation(user_id: int, prompt: str, orig_path: str, gen_path: str):
    """Log an image generation event."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (user_id, prompt, original_image_path, generated_image_path)
        VALUES (?, ?, ?, ?)
    ''', (user_id, prompt, orig_path, gen_path))
    conn.commit()
    conn.close()
