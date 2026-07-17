from database.connection import get_connection
from utils import hash_password, verify_password


def ensure_users_table():
    """Creates the users table if it doesn't already exist. Safe to call every startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            Username TEXT PRIMARY KEY,
            Password_Hash TEXT NOT NULL,
            Salt TEXT NOT NULL,
            Role TEXT NOT NULL,
            Full_Name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def seed_demo_users():
    """Creates 3 demo accounts if the users table is currently empty. Safe to call every startup."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # already seeded, don't overwrite

    demo_accounts = [
        ("admin", "admin123", "Admin", "Admin User"),
        ("teacher", "teacher123", "Teacher", "Demo Teacher"),
        ("accountant", "accountant123", "Accountant", "Demo Accountant"),
    ]

    for username, plain_password, role, full_name in demo_accounts:
        hashed, salt = hash_password(plain_password)
        cursor.execute("""
            INSERT INTO users (Username, Password_Hash, Salt, Role, Full_Name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hashed, salt, role, full_name))

    conn.commit()
    conn.close()


def authenticate(username, password):
    """Returns (role, full_name) if credentials are valid, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Password_Hash, Salt, Role, Full_Name FROM users WHERE Username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    stored_hash, salt, role, full_name = row
    if verify_password(password, salt, stored_hash):
        return role, full_name
    return None
