"""
One-time migration:
1. Adds a Room column to the existing timetable table, backfilled realistically
   (Science Lab for Physics/Chem/Bio/Science, Computer Lab for Computer Science,
   Playground for PE, Art Room for Art & Craft, otherwise a home classroom).
2. Creates the new timetable_overrides table for date-specific schedule changes.

Run from your project root:
    python migrate_timetable_overrides.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# --------------------------------------------------
# 1. Add Room to timetable
# --------------------------------------------------

cursor.execute("PRAGMA table_info(timetable)")
existing_columns = [row[1] for row in cursor.fetchall()]

if "Room" not in existing_columns:
    cursor.execute("ALTER TABLE timetable ADD COLUMN Room TEXT")
    print("Added column: Room")
else:
    print("Room column already exists, skipping.")

# Backfill rooms based on subject
SPECIAL_ROOMS = {
    "Physics": "Science Lab", "Chemistry": "Science Lab", "Biology": "Science Lab",
    "Science": "Science Lab", "Computer Science": "Computer Lab",
    "Physical Education": "Playground", "Art & Craft": "Art Room",
}

cursor.execute("""
    SELECT t.Timetable_ID, t.Class, t.Section, s.Subject_Name
    FROM timetable t
    JOIN subjects s ON t.Subject_ID = s.Subject_ID
    WHERE t.Room IS NULL
""")
rows = cursor.fetchall()

for timetable_id, cls, section, subject_name in rows:
    room = SPECIAL_ROOMS.get(subject_name, f"Room {100 + int(cls)}{section}")
    cursor.execute("UPDATE timetable SET Room = ? WHERE Timetable_ID = ?", (room, timetable_id))

print(f"Backfilled Room for {len(rows)} timetable rows.")

# --------------------------------------------------
# 2. Create timetable_overrides table
# --------------------------------------------------

cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetable_overrides (
        Override_ID INTEGER PRIMARY KEY,
        Class TEXT,
        Section TEXT,
        Date TEXT,
        Period INTEGER,
        Override_Type TEXT,
        New_Subject_ID INTEGER,
        New_Staff_ID TEXT,
        New_Room TEXT,
        Remarks TEXT
    )
""")
print("timetable_overrides table ready.")

conn.commit()
conn.close()
print("\nMigration complete.")
