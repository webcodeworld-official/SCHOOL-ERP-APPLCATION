from database.connection import get_connection
import pandas as pd
from datetime import date


def get_all_students():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM student", conn)
    conn.close()
    return df


def get_next_student_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(CAST(Student_ID AS INTEGER))
        FROM student
        WHERE Student_ID IS NOT NULL AND TRIM(Student_ID) != ''
    """)
    result = cursor.fetchone()[0]
    conn.close()

    if result is None:
        return 1001
    return int(result) + 1


def generate_admission_no(student_id, year):
    """Matches existing data pattern: ADM + year + Student_ID, e.g. ADM20261074."""
    return f"ADM{year}{student_id}"


def admission_exists(admission_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM student WHERE Admission_No = ?",
        (admission_no,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def roll_exists(roll_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM student WHERE Roll_No = ?",
        (roll_no,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def add_student(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student
        (
            Student_ID, Admission_No, Roll_No, First_Name, Last_Name,
            Gender, Date_of_Birth, Class, Section, House,
            Admission_Date, Academic_Year, Father_Name, Mother_Name,
            Parent_Mobile, Email, City, State, Transport_ID,
            Fee_Category, Blood_Group, Status
        )
        VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?,?,?, ?,?,?,?,?, ?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_student(student_id):
    """Returns a raw tuple. Prefer get_student_dict() for form pre-fill."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_student_dict(student_id):
    """Returns the student as a dict keyed by column name — used to pre-fill the edit form."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_student(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE student
        SET
            Admission_No=?, Roll_No=?, First_Name=?, Last_Name=?, Gender=?,
            Class=?, Section=?, Parent_Mobile=?, Status=?, Date_of_Birth=?,
            Blood_Group=?, Father_Name=?, Mother_Name=?, Email=?, City=?,
            State=?, House=?, Fee_Category=?
        WHERE Student_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE Student_ID=?", (int(student_id),))
    conn.commit()
    conn.close()


def get_current_academic_year():
    """e.g. '2026-2027' — matches existing data format."""
    today = date.today()
    if today.month >= 4:
        return f"{today.year}-{today.year + 1}"
    return f"{today.year - 1}-{today.year}"


def count_students_with_phone(phone, exclude_student_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_student_id:
        cursor.execute(
            "SELECT COUNT(*) FROM student WHERE Parent_Mobile = ? AND Student_ID != ?",
            (phone, exclude_student_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM student WHERE Parent_Mobile = ?",
            (phone,)
        )

    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_students_with_email(email, exclude_student_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_student_id:
        cursor.execute(
            "SELECT COUNT(*) FROM student WHERE Email = ? AND Student_ID != ?",
            (email, exclude_student_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM student WHERE Email = ?",
            (email,)
        )

    result = cursor.fetchone()[0]
    conn.close()
    return result