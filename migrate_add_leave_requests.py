"""
Creates the leave_requests table for staff leave applications.

Run from your project root:
    python migrate_add_leave_requests.py
"""

from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        Leave_ID INTEGER PRIMARY KEY,
        Staff_ID TEXT NOT NULL,
        Leave_Type TEXT,
        Start_Date TEXT,
        End_Date TEXT,
        Reason TEXT,
        Status TEXT DEFAULT 'Pending',
        Applied_Date TEXT,
        Reviewed_By TEXT,
        Review_Note TEXT,
        Branch_ID INTEGER
    )
""")

conn.commit()
conn.close()
print("leave_requests table ready.")
