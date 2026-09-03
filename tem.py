from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT Class, typeof(Class) FROM class_subjects LIMIT 5")
print(cursor.fetchall())
conn.close()