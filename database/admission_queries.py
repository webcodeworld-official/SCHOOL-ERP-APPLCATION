from database.connection import get_connection
import pandas as pd
from datetime import date


def get_all_admissions(branch_id=None):
    conn = get_connection()
    if branch_id is None:
        df = pd.read_sql("SELECT * FROM admission", conn)
    else:
        df = pd.read_sql("SELECT * FROM admission WHERE Branch_ID = ?", conn, params=(branch_id,))
    conn.close()
    return df


def get_students_without_admission_record(branch_id=None):
    conn = get_connection()
    if branch_id is None:
        query = """
            SELECT Student_ID, First_Name, Last_Name, Class, Section, Admission_Date, Stream, Transport_ID, Branch_ID
            FROM student
            WHERE Status = 'Active'
            AND Student_ID NOT IN (SELECT Student_ID FROM admission)
        """
        df = pd.read_sql(query, conn)
    else:
        query = """
            SELECT Student_ID, First_Name, Last_Name, Class, Section, Admission_Date, Stream, Transport_ID, Branch_ID
            FROM student
            WHERE Status = 'Active' AND Branch_ID = ?
            AND Student_ID NOT IN (SELECT Student_ID FROM admission)
        """
        df = pd.read_sql(query, conn, params=(branch_id,))
    conn.close()
    return df

def add_admission_record(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO admission
        (Admission_ID, Student_ID, Admission_Date, "ADMISSION MONTH-YEAR",
         Previous_School, Admission_Status, Entrance_Test, Admission_Fee, Branch_ID,
         Discount_Type, Entrance_Test_Score, Discount_Percentage)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
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
        SET Previous_School=?, Admission_Status=?, Entrance_Test=?, Admission_Fee=?,
            Discount_Type=?, Entrance_Test_Score=?, Discount_Percentage=?
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

DISCOUNT_TYPES = ["None", "Merit-Based", "Female Student", "Sports Achievement", "Sibling", "Staff Ward"]

FIXED_DISCOUNTS = {
    "None": 0,
    "Female Student": 5,
    "Sports Achievement": 10,
    "Sibling": 10,
    "Staff Ward": 15,
}


def calculate_merit_discount(score):
    """Merit-based discount tiers, based on entrance test score (0-100)."""
    if score is None:
        return 0
    if score >= 90:
        return 20
    elif score >= 85:
        return 10
    elif score >= 75:
        return 5
    return 0


def calculate_discount_percentage(discount_type, entrance_test_score=None):
    """Returns the discount % for whichever type was selected."""
    if discount_type == "Merit-Based":
        return calculate_merit_discount(entrance_test_score)
    return FIXED_DISCOUNTS.get(discount_type, 0)


def get_admission_discount_percentage(student_id):
    """Looks up a student's stored discount %, for use in Fee Management. Returns 0 if none."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Discount_Percentage FROM admission WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0