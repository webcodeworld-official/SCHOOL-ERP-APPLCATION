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
            Full_Name TEXT NOT NULL,
            Branch_ID INTEGER
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
    """Returns (role, full_name, branch_id) if credentials are valid, else None.
    branch_id is None for Admin (means: access to all branches)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Password_Hash, Salt, Role, Full_Name, Branch_ID FROM users WHERE Username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    stored_hash, salt, role, full_name, branch_id = row
    if verify_password(password, salt, stored_hash):
        return role, full_name, branch_id
    return None


def get_all_users():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql("SELECT Username, Role, Full_Name, Branch_ID FROM users", conn)
    conn.close()
    return df


def username_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE Username = ?", (username,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def create_user(username, password, role, full_name, branch_id=None):
    """branch_id should be None for Admin (all-branch access), or a specific Branch_ID otherwise."""
    hashed, salt = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (Username, Password_Hash, Salt, Role, Full_Name, Branch_ID)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, hashed, salt, role, full_name, branch_id))
    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE Username = ?", (username,))
    conn.commit()
    conn.close()


def count_admins():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE Role = 'Admin'")
    result = cursor.fetchone()[0]
    conn.close()
    return result
