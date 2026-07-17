from database.connection import get_connection
import pandas as pd
from datetime import date


def get_all_admissions():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM admission", conn)
    conn.close()
    return df


def get_students_without_admission_record():
    """Active students who don't yet have an admission record."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT Student_ID, First_Name, Last_Name, Class, Section, Admission_Date
        FROM student
        WHERE Status = 'Active'
        AND Student_ID NOT IN (SELECT Student_ID FROM admission)
    """, conn)
    conn.close()
    return df


def add_admission_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO admission
        (Admission_ID, Student_ID, Admission_Date, "ADMISSION MONTH-YEAR",
         Previous_School, Admission_Status, Entrance_Test, Admission_Fee)
        VALUES (?,?,?,?,?,?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_admission_dict(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admission WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_admission_record(data):
    """Edits process fields only. Admission_Date / year are locked after creation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE admission
        SET Previous_School=?, Admission_Status=?, Entrance_Test=?, Admission_Fee=?
        WHERE Student_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_admission_record(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admission WHERE Student_ID=?", (int(student_id),))
    conn.commit()
    conn.close()
