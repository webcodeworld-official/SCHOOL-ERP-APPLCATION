"""
One-time migration: adds a real Staff_ID column to the visitors table,
linking each visit to an actual staff record instead of loose text.
Backfills existing rows by matching Staff_Name against staff.Employee_Name.

Run from your project root:
    python migrate_visitor_staff_link.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(visitors)")
existing_columns = [row[1] for row in cursor.fetchall()]

if "Staff_ID" not in existing_columns:
    cursor.execute("ALTER TABLE visitors ADD COLUMN Staff_ID TEXT")
    print("Added column: Staff_ID")
else:
    print("Column already exists, skipping.")

# Backfill: match existing Staff_Name text to a real Staff_ID where possible
cursor.execute("SELECT Visitor_ID, Staff_Name FROM visitors WHERE Staff_ID IS NULL")
rows = cursor.fetchall()

matched, unmatched = 0, 0

for visitor_id, staff_name in rows:
    if not staff_name:
        unmatched += 1
        continue

    cursor.execute("SELECT Staff_ID FROM staff WHERE Employee_Name = ? LIMIT 1", (staff_name,))
    match = cursor.fetchone()

    if match:
        cursor.execute("UPDATE visitors SET Staff_ID = ? WHERE Visitor_ID = ?", (match[0], visitor_id))
        matched += 1
    else:
        unmatched += 1

conn.commit()
conn.close()

print(f"\nBackfill complete: {matched} matched, {unmatched} unmatched (no exact name match found).")
print("Unmatched rows will show blank 'Meeting With' until manually edited.")
