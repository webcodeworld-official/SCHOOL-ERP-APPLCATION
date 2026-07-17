from database.connection import get_connection
import pandas as pd

EXAM_NAMES = ["Unit Test 1", "Unit Test 2", "Mid Term", "Final Exam"]
SUBJECTS = ["English", "Math", "Science", "Social Studies", "Hindi", "Computer"]
PASS_THRESHOLD_PCT = 33


def grade_for(pct):
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= PASS_THRESHOLD_PCT: return "D"
    return "F"


def get_all_results():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM examination", conn)
    conn.close()
    return df


def get_next_result_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Result_ID) FROM examination")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def get_students_by_class_section(class_, section):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT Student_ID, First_Name, Last_Name, Roll_No
        FROM student
        WHERE Class = ? AND Section = ? AND Status = 'Active'
        ORDER BY CAST(Roll_No AS INTEGER)
    """, conn, params=(class_, section))
    conn.close()
    return df


def get_existing_marks(exam_name, subject, student_ids):
    """Returns existing Result rows for these students/exam/subject, keyed by Student_ID."""
    if not student_ids:
        return {}

    conn = get_connection()
    placeholders = ",".join(["?"] * len(student_ids))
    df = pd.read_sql(f"""
        SELECT * FROM examination
        WHERE Exam_Name = ? AND Subject = ? AND Student_ID IN ({placeholders})
    """, conn, params=[exam_name, subject] + student_ids)
    conn.close()

    return {row["Student_ID"]: row for _, row in df.iterrows()}


def upsert_marks(exam_name, subject, entries):
    """
    entries: list of dicts with Student_ID, Marks_Obtained, Total_Marks
    Inserts a new result if one doesn't exist for (Student_ID, Exam_Name, Subject),
    otherwise updates the existing one.
    """
    conn = get_connection()
    cursor = conn.cursor()

    for entry in entries:
        student_id = entry["Student_ID"]
        marks = entry["Marks_Obtained"]
        total = entry["Total_Marks"]
        pct = round((marks / total) * 100, 1) if total > 0 else 0
        grade = grade_for(pct)
        result = "Pass" if pct >= PASS_THRESHOLD_PCT else "Fail"

        cursor.execute("""
            SELECT Result_ID FROM examination
            WHERE Student_ID = ? AND Exam_Name = ? AND Subject = ?
        """, (student_id, exam_name, subject))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE examination
                SET Marks_Obtained=?, Total_Marks=?, Percentage=?, Grade=?, Result=?
                WHERE Result_ID=?
            """, (marks, total, pct, grade, result, existing[0]))
        else:
            cursor.execute("SELECT MAX(Result_ID) FROM examination")
            max_id = cursor.fetchone()[0]
            new_id = 1 if max_id is None else int(max_id) + 1

            cursor.execute("""
                INSERT INTO examination
                (Result_ID, Student_ID, Exam_Name, Subject, Marks_Obtained, Total_Marks, Percentage, Grade, Result)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (new_id, student_id, exam_name, subject, marks, total, pct, grade, result))

    conn.commit()
    conn.close()


def delete_result(result_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM examination WHERE Result_ID=?", (int(result_id),))
    conn.commit()
    conn.close()
