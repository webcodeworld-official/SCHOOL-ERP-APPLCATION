"""
Loads school_erp_realistic_data_v2.xlsx into your local school.db,
REPLACING all existing rows in each table.

Run this from your project root (where database/connection.py lives):
    python load_school_data_v2.py
"""

import pandas as pd
from database.connection import get_connection

EXCEL_PATH = "school_erp_realistic_data_v2.xlsx"

# --------------------------------------------------
# CREATE TABLE statements for the 4 NEW tables
# (the original 9 already exist in your live school.db)
# --------------------------------------------------

CREATE_STATEMENTS = {
    "subjects": """
        CREATE TABLE IF NOT EXISTS subjects (
            Subject_ID INTEGER PRIMARY KEY,
            Subject_Name TEXT,
            Subject_Code TEXT,
            Type TEXT
        )
    """,
    "class_subjects": """
        CREATE TABLE IF NOT EXISTS class_subjects (
            Class TEXT,
            Subject_ID INTEGER
        )
    """,
    "teacher_assignments": """
        CREATE TABLE IF NOT EXISTS teacher_assignments (
            Assignment_ID INTEGER PRIMARY KEY,
            Class TEXT,
            Section TEXT,
            Subject_ID INTEGER,
            Staff_ID TEXT
        )
    """,
    "timetable": """
        CREATE TABLE IF NOT EXISTS timetable (
            Timetable_ID INTEGER PRIMARY KEY,
            Class TEXT,
            Section TEXT,
            Day TEXT,
            Period INTEGER,
            Subject_ID INTEGER,
            Staff_ID TEXT
        )
    """,
}

TABLES = {
    "student": {"sheet": "STUDENT", "int_cols": ["Student_ID", "Class", "Parent_Mobile", "Transport_ID"]},
    "staff": {"sheet": "STAFF", "int_cols": ["Experience_Yrs", "Salary", "Phone"]},
    "visitors": {"sheet": "VISITORS", "int_cols": ["Visitor_ID", "Student_ID"]},
    "transportation": {"sheet": "TRANSPORTATION", "int_cols": ["Transport_ID", "Student_ID", "Driver_Phone", "Distance_KM", "Transport_Fee"]},
    "admission": {"sheet": "ADMISSION", "int_cols": ["Student_ID", "ADMISSION MONTH-YEAR", "Admission_Fee"]},
    "library": {"sheet": "LIBRARY", "int_cols": ["Transaction_ID", "Student_ID", "Book_ID", "Fine"]},
    "attendence": {"sheet": "ATTENDANCE", "int_cols": ["Attendance_ID", "Student_ID", "Class"]},
    "fees": {"sheet": "FEES", "int_cols": ["Payment_ID", "Student_ID", "Tuition_Fee", "Transport_Fee",
                                             "Library_Fee", "Exam_Fee", "Discount", "Total_Fee",
                                             "Amount_Paid", "Balance"]},
    "examination": {"sheet": "EXAMINATION", "int_cols": ["Result_ID", "Student_ID", "Marks_Obtained", "Total_Marks", "Percentage"]},
    "subjects": {"sheet": "SUBJECTS", "int_cols": ["Subject_ID"]},
    "class_subjects": {"sheet": "CLASS_SUBJECTS", "int_cols": ["Subject_ID"], "str_cols": ["Class"]},
    "teacher_assignments": {"sheet": "TEACHER_ASSIGNMENTS", "int_cols": ["Assignment_ID", "Subject_ID"], "str_cols": ["Class", "Section", "Staff_ID"]},
    "timetable": {"sheet": "TIMETABLE", "int_cols": ["Timetable_ID", "Period", "Subject_ID"], "str_cols": ["Class", "Section", "Staff_ID"]},
}


def clean_value(val, is_int, is_str):
    if pd.isna(val):
        return None
    if is_int:
        return int(val)
    if is_str:
        return str(val)
    return val


def load_table(conn, table_name, config):
    df = pd.read_excel(EXCEL_PATH, sheet_name=config["sheet"])
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")

    columns = df.columns.tolist()
    placeholders = ",".join(["?"] * len(columns))
    col_names = ",".join([f'"{c}"' for c in columns])
    int_cols = set(config["int_cols"])
    str_cols = set(config.get("str_cols", []))

    rows_to_insert = []
    for _, row in df.iterrows():
        values = [clean_value(row[col], col in int_cols, col in str_cols) for col in columns]
        rows_to_insert.append(tuple(values))

    cursor.executemany(
        f'INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})',
        rows_to_insert
    )
    conn.commit()
    print(f"  {table_name}: {len(rows_to_insert)} rows loaded")


def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("Ensuring new Academic Structure tables exist...")
    for table_name, create_sql in CREATE_STATEMENTS.items():
        cursor.execute(create_sql)
    conn.commit()
    print("Done.\n")

    print(f"Loading data from {EXCEL_PATH} into school.db...")
    print("(this will DELETE existing rows in each table first)\n")

    for table_name, config in TABLES.items():
        load_table(conn, table_name, config)

    conn.close()
    print("\nDone. All 13 tables loaded, including new Academic Structure data.")


if __name__ == "__main__":
    main()
