import pandas as pd
from database.connection import get_connection

conn = get_connection()

# Show all tables
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)

print("Tables in database:")
print(tables)

print("\n----------------------------\n")

# Display student data
student_df = pd.read_sql(
    "SELECT * FROM student LIMIT 5",
    conn
)

print(student_df)

conn.close()
