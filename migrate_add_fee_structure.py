"""
Fee Structure foundation migration:
1. Creates fee_types (master list of what can be charged).
2. Creates fee_structure (per Class/Stream/Academic Year template amounts).
3. Adds Hostel_Fee, Books_Fee, Due_Date, Late_Fine columns to the existing
   fees table (backward compatible — existing rows default to 0/NULL).

Run from your project root:
    python migrate_add_fee_structure.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# --------------------------------------------------
# 1. fee_types
# --------------------------------------------------

cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_types (
        Fee_Type_ID INTEGER PRIMARY KEY,
        Fee_Type_Name TEXT NOT NULL,
        Is_Optional TEXT NOT NULL
    )
""")

cursor.execute("SELECT COUNT(*) FROM fee_types")
if cursor.fetchone()[0] == 0:
    default_types = [
        (1, "Tuition", "N"),
        (2, "Transport", "Y"),
        (3, "Library", "N"),
        (4, "Exam", "N"),
        (5, "Hostel", "Y"),
        (6, "Books", "Y"),
        (7, "Development", "N"),
        (8, "Activity", "Y"),
    ]
    cursor.executemany(
        "INSERT INTO fee_types (Fee_Type_ID, Fee_Type_Name, Is_Optional) VALUES (?,?,?)",
        default_types
    )
    print("Seeded 8 default fee types.")
else:
    print("fee_types already has data, skipping seed.")

# --------------------------------------------------
# 2. fee_structure
# --------------------------------------------------

cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_structure (
        Structure_ID INTEGER PRIMARY KEY,
        Class TEXT NOT NULL,
        Stream TEXT,
        Academic_Year TEXT NOT NULL,
        Fee_Type_ID INTEGER NOT NULL,
        Amount INTEGER NOT NULL,
        Branch_ID INTEGER
    )
""")
print("fee_structure table ready.")

# --------------------------------------------------
# 3. Extend fees table
# --------------------------------------------------

cursor.execute("PRAGMA table_info(fees)")
existing_columns = [row[1] for row in cursor.fetchall()]

new_columns = {
    "Hostel_Fee": "INTEGER DEFAULT 0",
    "Books_Fee": "INTEGER DEFAULT 0",
    "Due_Date": "TEXT",
    "Late_Fine": "INTEGER DEFAULT 0",
}

for col_name, col_def in new_columns.items():
    if col_name not in existing_columns:
        cursor.execute(f"ALTER TABLE fees ADD COLUMN {col_name} {col_def}")
        print(f"Added column to fees: {col_name}")
    else:
        print(f"fees already has {col_name}, skipping.")

conn.commit()
conn.close()
print("\nMigration complete.")
