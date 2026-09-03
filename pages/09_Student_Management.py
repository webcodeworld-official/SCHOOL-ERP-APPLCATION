import streamlit as st
import io
from database.student_queries import get_all_students
from components.student_cards import show_student_cards
from components.student_table import show_student_table
from components.dialogs import (
    add_student_dialog,
    edit_student_dialog,
    delete_student_dialog
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

students = get_all_students(branch_id=st.session_state.get("active_branch_id"))

from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

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
# KPI CARDS
# --------------------------------------------------

show_student_cards(students)

st.divider()

# --------------------------------------------------
# SEARCH & FILTERS
# --------------------------------------------------

col_search, col_class, col_section, col_sort, col_order = st.columns([2, 1, 1, 1, 0.7])

with col_search:
    search = st.text_input(
        "🔍 Search Student",
        placeholder="Search by Student ID, Admission No, Roll No or Name..."
    )

with col_class:
    class_options = ["All"] + sorted(students["Class"].dropna().unique().tolist(), key=int)
    selected_class = st.selectbox("Class", class_options)

with col_section:
    section_options = ["All"] + sorted(students["Section"].dropna().unique().tolist())
    selected_section = st.selectbox("Section", section_options)

with col_sort:
    sort_by = st.selectbox(
        "Sort by",
        ["Roll_No", "Full_Name", "Class", "Admission_No"]
    )

with col_order:
    st.write("")  # spacer to align with the selectbox label above
    descending = st.toggle("⬇️ Desc")

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_students = students.copy()

if search:
    filtered_students = filtered_students[
        filtered_students["Student_ID"].astype(str).str.contains(search, case=False, na=False)
        | filtered_students["Admission_No"].astype(str).str.contains(search, case=False, na=False)
        | filtered_students["Roll_No"].astype(str).str.contains(search, case=False, na=False)
        | filtered_students["Full_Name"].str.contains(search, case=False, na=False)
    ]

if selected_class != "All":
    filtered_students = filtered_students[filtered_students["Class"] == selected_class]

if selected_section != "All":
    filtered_students = filtered_students[filtered_students["Section"] == selected_section]

filtered_students = filtered_students.sort_values(by=sort_by, ascending=not descending)
# --------------------------------------------------
# STUDENT TABLE
# --------------------------------------------------

st.caption(f"Showing {len(filtered_students)} students")

selected_student = show_student_table(filtered_students)

if selected_student is None or (hasattr(selected_student, "__len__") and len(selected_student) == 0):
    selected_student = []

st.divider()

# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

btn1, btn2, btn3, btn4 = st.columns([1.2, 1.2, 1.2, 1.2])

with btn1:
    if st.button("➕ Add Student", use_container_width=True):
        add_student_dialog()

with btn2:
    edit_clicked = st.button(
        "✏️ Edit",
        use_container_width=True,
        disabled=len(selected_student) == 0
    )
    if edit_clicked:
        edit_student_dialog(selected_student)

with btn3:
    delete_clicked = st.button(
        "🗑 Delete",
        use_container_width=True,
        disabled=len(selected_student) == 0
    )
    if delete_clicked:
        delete_student_dialog(selected_student)

import io

...

with btn4:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_students)} student(s)")

        # Excel export
        excel_buffer = io.BytesIO()
        filtered_students.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="students_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # CSV export
        csv_data = filtered_students.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="students_export.csv",
            mime="text/csv",
            use_container_width=True
        )

