import streamlit as st
from datetime import date
from database.student_queries import (
    add_student, update_student, delete_student,
    get_next_student_id, roll_exists, generate_admission_no,
    get_current_academic_year, get_student_dict,
    count_students_with_phone, count_students_with_email
)
from components.student_form import student_form
from utils import is_valid_phone, is_valid_email


@st.dialog("ℹ️ Message")
def message_dialog(title, message, icon="✅"):
    st.subheader(f"{icon} {title}")
    st.write(message)

    if st.button("OK", use_container_width=True):
        st.rerun()


@st.dialog("⚠️ Confirmation")
def confirm_dialog(message):
    st.warning(message)

    col1, col2 = st.columns(2)

    with col1:
        yes = st.button("Yes", use_container_width=True)

    with col2:
        no = st.button("No", use_container_width=True)

    if yes:
        return True

    if no:
        st.rerun()

    return False

@st.dialog("➕ Add Student")
def add_student_dialog():

    next_id = get_next_student_id()
    next_admission_no = generate_admission_no(next_id, date.today().year)

    preview = {
        "Student_ID": next_id,
        "Admission_No": next_admission_no,
    }

    data = student_form(preview)

    if st.button("Save", use_container_width=True):

        if not data["First_Name"]:
            st.error("First Name is required.")
            return

        if not data["Roll_No"]:
            st.error("Roll Number is required.")
            return

        if roll_exists(data["Roll_No"]):
            st.error("This Roll Number already exists.")
            return

        if not is_valid_phone(data["Parent_Mobile"]):
            st.error("Enter a valid 10-digit mobile number (starting 6-9).")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if count_students_with_phone(data["Parent_Mobile"]) > 0:
            st.warning("⚠️ This phone number is already used by another student (e.g. a sibling).")

        if data["Email"] and count_students_with_email(data["Email"]) > 0:
            st.warning("⚠️ This email is already used by another student.")

        values = (
            next_id,
            next_admission_no,
            data["Roll_No"],
            data["First_Name"],
            data["Last_Name"],
            data["Gender"],
            str(data["Date_of_Birth"]),
            data["Class"],
            data["Section"],
            data["House"],
            str(date.today()),
            get_current_academic_year(),
            data["Father_Name"],
            data["Mother_Name"],
            data["Parent_Mobile"],
            data["Email"],
            data["City"],
            data["State"],
            None,
            data["Fee_Category"],
            data["Blood_Group"],
            data["Status"],
        )

        add_student(values)
        st.success(f"Student added successfully. Admission No: {next_admission_no}")
        st.rerun()

@st.dialog("✏️ Edit Student")
def edit_student_dialog(selected_student):
    student_id = int(selected_student["Student_ID"])
    full_student = get_student_dict(student_id)  # fetch ALL fields, not just table columns

    data = student_form(full_student)

    if st.button("Update", use_container_width=True):

        if not data["Roll_No"]:
            st.error("Roll Number is required.")
            return

        if not is_valid_phone(data["Parent_Mobile"]):
            st.error("Enter a valid 10-digit mobile number (starting 6-9).")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if count_students_with_phone(data["Parent_Mobile"], exclude_student_id=student_id) > 0:
            st.warning("⚠️ This phone number is already used by another student.")

        if data["Email"] and count_students_with_email(data["Email"], exclude_student_id=student_id) > 0:
            st.warning("⚠️ This email is already used by another student.")

        values = (
            full_student["Admission_No"],  # unchanged — Admission_No is never editable
            data["Roll_No"],
            data["First_Name"],
            data["Last_Name"],
            data["Gender"],
            data["Class"],
            data["Section"],
            data["Parent_Mobile"],
            data["Status"],
            str(data["Date_of_Birth"]),
            data["Blood_Group"],
            data["Father_Name"],
            data["Mother_Name"],
            data["Email"],
            data["City"],
            data["State"],
            data["House"],
            data["Fee_Category"],
            student_id,
        )

        update_student(values)
        st.success("Student updated successfully.")
        st.rerun()


@st.dialog("🗑 Delete Student")
def delete_student_dialog(selected_student):
    st.warning(
        f"Are you sure you want to delete **{selected_student['Full_Name']}** "
        f"(Student ID: {selected_student['Student_ID']})? This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_student(int(selected_student["Student_ID"]))
            st.success("Student deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()