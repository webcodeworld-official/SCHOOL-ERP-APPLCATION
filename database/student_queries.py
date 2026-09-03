from database.connection import get_connection
import pandas as pd
from datetime import date
import os

PHOTO_DIR = "assets/student_photos"
DOCUMENT_DIR = "assets/student_documents"


def ensure_upload_dirs():
    os.makedirs(PHOTO_DIR, exist_ok=True)
    os.makedirs(DOCUMENT_DIR, exist_ok=True)


def save_uploaded_file(uploaded_file, student_id, folder, prefix):
    """Saves an uploaded file to disk, returns the relative path. Returns None if no file given."""
    if uploaded_file is None:
        return None

    ensure_upload_dirs()
    ext = uploaded_file.name.split(".")[-1]
    filename = f"{prefix}_{student_id}.{ext}"
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return filepath


def get_all_students(branch_id=None):
    """If branch_id is None, returns students across ALL branches (Admin's 'All Branches' view).
    Otherwise, only that branch's students."""
    conn = get_connection()
    if branch_id is None:
        df = pd.read_sql("SELECT * FROM student", conn)
    else:
        df = pd.read_sql("SELECT * FROM student WHERE Branch_ID = ?", conn, params=(branch_id,))
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
    return 1001 if result is None else int(result) + 1


def generate_admission_no(student_id, year):
    return f"ADM{year}{student_id}"


def roll_exists(roll_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM student WHERE Roll_No = ?", (roll_no,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def add_student(data):
    """data is a tuple matching the column order below, including the 3 new columns at the end."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student
        (
            Student_ID, Admission_No, Roll_No, First_Name, Last_Name,
            Gender, Date_of_Birth, Class, Section, House,
            Admission_Date, Academic_Year, Father_Name, Mother_Name,
            Parent_Mobile, Email, City, State, Transport_ID,
            Fee_Category, Blood_Group, Status, Photo_Path, Aadhar_No, Aadhar_Doc_Path,
            Stream, Branch_ID
        )
        VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?,?,?, ?,?,?,?,?, ?,?,?,?,?,?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_student_dict(student_id):
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
    """data is a tuple matching the SET order below, including the 3 new columns, ending with Student_ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE student
        SET
            Admission_No=?, Roll_No=?, First_Name=?, Last_Name=?, Gender=?,
            Class=?, Section=?, Parent_Mobile=?, Status=?, Date_of_Birth=?,
            Blood_Group=?, Father_Name=?, Mother_Name=?, Email=?, City=?,
            State=?, House=?, Fee_Category=?, Aadhar_No=?, Photo_Path=?, Aadhar_Doc_Path=?,
            Stream=?
        WHERE Student_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE Student_ID=?", (student_id,))
    conn.commit()
    conn.close()


def get_current_academic_year():
    today = date.today()
    if today.month >= 4:
        return f"{today.year}-{today.year + 1}"
    return f"{today.year - 1}-{today.year}"


def count_students_with_phone(phone, exclude_student_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_student_id:
        cursor.execute("SELECT COUNT(*) FROM student WHERE Parent_Mobile = ? AND Student_ID != ?", (phone, exclude_student_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM student WHERE Parent_Mobile = ?", (phone,))
    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_students_with_email(email, exclude_student_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_student_id:
        cursor.execute("SELECT COUNT(*) FROM student WHERE Email = ? AND Student_ID != ?", (email, exclude_student_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM student WHERE Email = ?", (email,))
    result = cursor.fetchone()[0]
    conn.close()
    return result
