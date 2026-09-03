"""
Adds discount-calculation fields to the admission table:
- Discount_Type: which category of discount was selected
- Entrance_Test_Score: numeric percentage (only relevant for Merit-Based)
- Discount_Percentage: the calculated result, stored for reuse in Fee Management

Run from your project root:
    python migrate_add_admission_discount.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(admission)")
existing_columns = [row[1] for row in cursor.fetchall()]

new_columns = {
    "Discount_Type": "TEXT",
    "Entrance_Test_Score": "INTEGER",
    "Discount_Percentage": "INTEGER",
}

for col_name, col_type in new_columns.items():
    if col_name not in existing_columns:
        cursor.execute(f"ALTER TABLE admission ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists, skipping: {col_name}")

conn.commit()
conn.close()
print("\nMigration complete.")
