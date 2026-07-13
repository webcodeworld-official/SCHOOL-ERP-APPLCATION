import streamlit as st
import pandas as pd
from components.students_table import show_student_table
from database.student_queries import (
    get_all_students,
    add_student
)
from components.students_dialogs import add_student_dialog
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Management",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

students = get_all_students()

# Create Full Name column
students["Full_Name"] = (
    students["First_Name"].fillna("")
    + " "
    + students["Last_Name"].fillna("")
)

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🎓 Student Management")

st.caption("Manage all student records from the database.")

st.divider()

# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

btn1, btn2, btn3 = st.columns([1,1,6])

with btn1:
    if st.button("➕ Add Student"):
        add_student_dialog()

with btn2:
    st.button("📤 Export CSV")

st.divider()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

from components.students_cards import show_student_cards
show_student_cards(students)

st.divider()

# --------------------------------------------------
# SEARCH BOX
# --------------------------------------------------

search = st.text_input(
    "🔍 Search Student",
    placeholder="Search by Student ID, Admission No, Roll No or Name..."
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_students = students.copy()

if search:

    filtered_students = students[
        students["Student_ID"].astype(str).str.contains(search, case=False, na=False)
        |
        students["Admission_No"].astype(str).str.contains(search, case=False, na=False)
        |
        students["Roll_No"].astype(str).str.contains(search, case=False, na=False)
        |
        students["Full_Name"].str.contains(search, case=False, na=False)
    ]

# --------------------------------------------------
# STUDENT TABLE
# --------------------------------------------------

show_student_table(filtered_students)