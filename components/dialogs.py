import streamlit as st
from datetime import date
from database.student_queries import (
    add_student, update_student, delete_student,
    get_next_student_id, roll_exists, generate_admission_no,
    get_current_academic_year, get_student_dict,
    count_students_with_phone, count_students_with_email,
    save_uploaded_file
)
from components.student_form import student_form
from utils import is_valid_phone, is_valid_email
import re


def is_valid_aadhar(aadhar_no):
    """Aadhar is exactly 12 digits. Empty is allowed (optional field)."""
    if not aadhar_no:
        return True
    return bool(re.fullmatch(r"\d{12}", aadhar_no.strip()))


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
    admission_year = date.today().year
    next_admission_no = generate_admission_no(next_id, admission_year)

    preview = {"Student_ID": next_id, "Admission_No": next_admission_no}

    data = student_form(preview)

    active_branch_id = st.session_state.get("active_branch_id")
    if active_branch_id is None:
        from database.branch_queries import get_all_branches
        branches = get_all_branches()
        if branches.empty:
            st.error("No branches exist yet. Add a branch first (Settings).")
            branch_id_for_new_student = None
        else:
            branch_choice = st.selectbox(
                "Assign to Branch",
                branches["Branch_Name"].tolist(),
                key="add_student_branch_pick"
            )
            branch_id_for_new_student = int(
                branches[branches["Branch_Name"] == branch_choice]["Branch_ID"].iloc[0]
            )
    else:
        branch_id_for_new_student = active_branch_id

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

        from utils import format_and_validate_phone
        formatted_phone, phone_valid = format_and_validate_phone(
            data["Parent_Mobile_Raw"], data["Parent_Mobile_Region"]
        )
        if not phone_valid:
            st.error("Enter a valid phone number for the selected country.")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if not is_valid_aadhar(data["Aadhar_No"]):
            st.error("Aadhar Number must be exactly 12 digits.")
            return

        if branch_id_for_new_student is None:
            st.error("A branch must be selected.")
            return

        if count_students_with_phone(formatted_phone) > 0:
            st.warning("⚠️ This phone number is already used by another student (e.g. a sibling).")

        if data["Email"] and count_students_with_email(data["Email"]) > 0:
            st.warning("⚠️ This email is already used by another student.")

        photo_path = save_uploaded_file(data["Photo_File"], next_id, "assets/student_photos", "photo")
        aadhar_doc_path = save_uploaded_file(data["Aadhar_Doc_File"], next_id, "assets/student_documents", "aadhar")

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
            formatted_phone,
            data["Email"],
            data["City"],
            data["State"],
            None,
            data["Fee_Category"],
            data["Blood_Group"],
            data["Status"],
            photo_path,
            data["Aadhar_No"],
            aadhar_doc_path,
            data["Stream"],
            branch_id_for_new_student,
        )

        add_student(values)
        st.success(f"Student added successfully. Admission No: {next_admission_no}")
        st.rerun()

@st.dialog("✏️ Edit Student")
def edit_student_dialog(selected_student):
    student_id = int(selected_student["Student_ID"])
    full_student = get_student_dict(student_id)

    data = student_form(full_student)

    if st.button("Update", use_container_width=True):

        if not data["Roll_No"]:
            st.error("Roll Number is required.")
            return

        from utils import format_and_validate_phone
        formatted_phone, phone_valid = format_and_validate_phone(
            data["Parent_Mobile_Raw"], data["Parent_Mobile_Region"]
        )
        if not phone_valid:
            st.error("Enter a valid phone number for the selected country.")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if not is_valid_aadhar(data["Aadhar_No"]):
            st.error("Aadhar Number must be exactly 12 digits.")
            return

        if count_students_with_phone(formatted_phone, exclude_student_id=student_id) > 0:
            st.warning("⚠️ This phone number is already used by another student.")

        if data["Email"] and count_students_with_email(data["Email"], exclude_student_id=student_id) > 0:
            st.warning("⚠️ This email is already used by another student.")

        photo_path = save_uploaded_file(data["Photo_File"], student_id, "assets/student_photos", "photo")
        if photo_path is None:
            photo_path = full_student.get("Photo_Path")

        aadhar_doc_path = save_uploaded_file(data["Aadhar_Doc_File"], student_id, "assets/student_documents", "aadhar")
        if aadhar_doc_path is None:
            aadhar_doc_path = full_student.get("Aadhar_Doc_Path")

        values = (
            data["Admission_No"],
            data["Roll_No"],
            data["First_Name"],
            data["Last_Name"],
            data["Gender"],
            data["Class"],
            data["Section"],
            formatted_phone,
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
            data["Aadhar_No"],
            photo_path,
            aadhar_doc_path,
            data["Stream"],
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
            delete_student(selected_student["Student_ID"])
            st.success("Student deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
