"""
One-time migration: adds Photo_Path, Aadhar_No, Aadhar_Doc_Path columns
to the existing student table. Safe to run multiple times (checks first).

Run from your project root:
    python migrate_add_student_documents.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(student)")
existing_columns = [row[1] for row in cursor.fetchall()]

new_columns = {
    "Photo_Path": "TEXT",
    "Aadhar_No": "TEXT",
    "Aadhar_Doc_Path": "TEXT",
}

for col_name, col_type in new_columns.items():
    if col_name not in existing_columns:
        cursor.execute(f"ALTER TABLE student ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists, skipping: {col_name}")

conn.commit()
conn.close()
print("\nMigration complete.")
