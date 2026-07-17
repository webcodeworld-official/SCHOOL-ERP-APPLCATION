"""
Loads school_erp_realistic_data.xlsx into your local school.db,
REPLACING all existing rows in each of the 9 tables.

Run this from your project root (where database/connection.py lives):
    python load_school_data.py

Requires: school_erp_realistic_data.xlsx in the same folder as this script
(or update EXCEL_PATH below to point to wherever you saved it).
"""

import pandas as pd
from database.connection import get_connection

EXCEL_PATH = "school_erp_realistic_data.xlsx"

# Table name -> (Excel sheet name, columns that must be cast to int, columns that may be null/None)
TABLES = {
    "student": {
        "sheet": "STUDENT",
        "int_cols": ["Student_ID", "Class", "Parent_Mobile", "Transport_ID"],
        "nullable_int_cols": ["Transport_ID"],
    },
    "staff": {
        "sheet": "STAFF",
        "int_cols": ["Experience_Yrs", "Salary", "Phone"],
        "nullable_int_cols": [],
    },
    "visitors": {
        "sheet": "VISITORS",
        "int_cols": ["Visitor_ID", "Student_ID"],
        "nullable_int_cols": ["Student_ID"],
    },
    "transportation": {
        "sheet": "TRANSPORTATION",
        "int_cols": ["Transport_ID", "Student_ID", "Driver_Phone", "Distance_KM", "Transport_Fee"],
        "nullable_int_cols": [],
    },
    "admission": {
        "sheet": "ADMISSION",
        "int_cols": ["Student_ID", "ADMISSION MONTH-YEAR", "Admission_Fee"],
        "nullable_int_cols": [],
    },
    "library": {
        "sheet": "LIBRARY",
        "int_cols": ["Transaction_ID", "Student_ID", "Book_ID", "Fine"],
        "nullable_int_cols": ["Fine"],
    },
    "attendence": {
        "sheet": "ATTENDANCE",
        "int_cols": ["Attendance_ID", "Student_ID", "Class"],
        "nullable_int_cols": [],
    },
    "fees": {
        "sheet": "FEES",
        "int_cols": ["Payment_ID", "Student_ID", "Tuition_Fee", "Transport_Fee",
                     "Library_Fee", "Exam_Fee", "Discount", "Total_Fee",
                     "Amount_Paid", "Balance"],
        "nullable_int_cols": [],
    },
    "examination": {
        "sheet": "EXAMINATION",
        "int_cols": ["Result_ID", "Student_ID", "Marks_Obtained", "Total_Marks", "Percentage"],
        "nullable_int_cols": [],
    },
}


def clean_value(val, is_int, is_nullable):
    """Convert pandas/NaN values into proper None or int for SQLite."""
    if pd.isna(val):
        return None
    if is_int:
        return int(val)
    return val


def load_table(conn, table_name, config):
    df = pd.read_excel(EXCEL_PATH, sheet_name=config["sheet"])

    cursor = conn.cursor()

    # Wipe existing rows first — this REPLACES the old sample data
    cursor.execute(f"DELETE FROM {table_name}")

    columns = df.columns.tolist()
    placeholders = ",".join(["?"] * len(columns))
    col_names = ",".join([f'"{c}"' for c in columns])

    int_cols = set(config["int_cols"])

    rows_to_insert = []
    for _, row in df.iterrows():
        values = []
        for col in columns:
            is_int = col in int_cols
            values.append(clean_value(row[col], is_int, True))
        rows_to_insert.append(tuple(values))

    cursor.executemany(
        f'INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})',
        rows_to_insert
    )

    conn.commit()
    print(f"  {table_name}: {len(rows_to_insert)} rows loaded")


def main():
    conn = get_connection()

    print(f"Loading data from {EXCEL_PATH} into school.db...")
    print("(this will DELETE existing rows in each table first)\n")

    for table_name, config in TABLES.items():
        load_table(conn, table_name, config)

    conn.close()
    print("\nDone. All 9 tables replaced with realistic data.")


if __name__ == "__main__":
    main()
