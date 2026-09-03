from database.connection import get_connection
import pandas as pd


def get_all_branches():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM branches ORDER BY Branch_Name", conn)
    conn.close()
    return df


def get_branch_name(branch_id):
    if branch_id is None:
        return "All Branches"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Branch_Name FROM branches WHERE Branch_ID = ?", (branch_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown Branch"


def get_next_branch_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Branch_ID) FROM branches")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def add_branch(name, address, city, phone, principal_name):
    conn = get_connection()
    cursor = conn.cursor()
    branch_id = get_next_branch_id()
    cursor.execute("""
        INSERT INTO branches (Branch_ID, Branch_Name, Address, City, Phone, Principal_Name)
        VALUES (?,?,?,?,?,?)
    """, (branch_id, name, address, city, phone, principal_name))
    conn.commit()
    conn.close()
    return branch_id
