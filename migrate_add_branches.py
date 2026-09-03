"""
Multi-branch foundation migration:
1. Creates the branches table.
2. Seeds a default "Main Branch" (Branch_ID=1) so all your EXISTING data
   gets assigned to it automatically (nothing breaks or goes missing).
3. Adds Branch_ID to every branch-scoped table, defaulting existing rows to 1.
4. Adds Branch_ID to users (NULL = Admin with access to all branches).

Run from your project root:
    python migrate_add_branches.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        Branch_ID INTEGER PRIMARY KEY,
        Branch_Name TEXT NOT NULL,
        Address TEXT,
        City TEXT,
        Phone TEXT,
        Principal_Name TEXT
    )
""")

cursor.execute("SELECT COUNT(*) FROM branches")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO branches (Branch_ID, Branch_Name, Address, City, Phone, Principal_Name)
        VALUES (1, 'Main Branch', '', '', '', '')
    """)
    print("Seeded default 'Main Branch' (Branch_ID=1).")
else:
    print("Branches table already has data, skipping seed.")

TABLES_NEEDING_BRANCH = [
    "student", "staff", "admission", "transportation",
    "visitors", "library", "teacher_assignments",
    "timetable", "timetable_overrides",
]

for table in TABLES_NEEDING_BRANCH:
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "Branch_ID" not in existing_columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN Branch_ID INTEGER DEFAULT 1")
        print(f"Added Branch_ID to {table} (existing rows defaulted to Branch 1).")
    else:
        print(f"{table} already has Branch_ID, skipping.")

cursor.execute("PRAGMA table_info(users)")
existing_columns = [row[1] for row in cursor.fetchall()]

if "Branch_ID" not in existing_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN Branch_ID INTEGER")
    print("Added Branch_ID to users (NULL by default = unrestricted).")
    cursor.execute("UPDATE users SET Branch_ID = 1 WHERE Role != 'Admin' AND Branch_ID IS NULL")
else:
    print("users already has Branch_ID, skipping.")

conn.commit()
conn.close()
print("\nMigration complete. All existing data is now under 'Main Branch' (Branch_ID=1).")
