from database.connection import get_connection
import pandas as pd


def get_all_students():
    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM student",
        conn
    )

    conn.close()

    return df

def get_next_student_id():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(Student_ID)
        FROM student
    """)

    result = cursor.fetchone()[0]

    conn.close()

    if result is None:
        return 1001

    return result + 1



def add_student(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student
        (
            Student_ID,
            Admission_No,
            Roll_No,
            First_Name,
            Last_Name,
            Gender,
            Date_of_Birth,
            Class,
            Section,
            House,
            Admission_Date,
            Academic_Year,
            Father_Name,
            Mother_Name,
            Parent_Mobile,
            Email,
            City,
            State,
            Transport_ID,
            Fee_Category,
            Blood_Group,
            Status
        )

        VALUES

        (
            ?,?,?,?,?,?,
            ?,?,?,?,?,?,
            ?,?,?,?,?,?,
            ?,?,?,?
        )
    """, data)

    conn.commit()

    conn.close()
