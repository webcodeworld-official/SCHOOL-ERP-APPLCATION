"""
Adds a Stream column to the student table (Science/Commerce/Arts),
relevant only for Class 11-12.

Run from your project root:
    python migrate_add_stream.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(student)")
existing_columns = [row[1] for row in cursor.fetchall()]

if "Stream" not in existing_columns:
    cursor.execute("ALTER TABLE student ADD COLUMN Stream TEXT")
    print("Added column: Stream")
else:
    print("Stream column already exists, skipping.")

conn.commit()
conn.close()
print("Migration complete.")
