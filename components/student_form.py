import streamlit as st
from datetime import date, datetime


def _parse_date(value, default):
    """Safely parse a date string from the DB into a date object."""
    if not value:
        return default
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return default


def student_form(student=None):
    """
    Reusable Student Form.

    If student=None  -> Add Student
    If student has data -> Edit Student

    Returns dictionary containing all entered values.
    """

    if student is None:
        student = {}

    # Unique suffix for widget keys — uses Student_ID if editing, "new" if adding.
    # Prevents duplicate-element-id errors if this form is ever rendered more than once per run.
    key_suffix = str(student.get("Student_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        student_id = st.text_input(
            "Student ID",
            value=str(student.get("Student_ID", "")),
            disabled=True,
            key=f"student_id_{key_suffix}"
        )

        admission_no = st.text_input(
            "Admission Number",
            value=str(student.get("Admission_No", "")),
            disabled=True,
            key=f"admission_no_{key_suffix}"
        )

        roll_no = st.text_input(
            "Roll Number",
            value=str(student.get("Roll_No", "")),
            key=f"roll_no_{key_suffix}"
        )

        first_name = st.text_input(
            "First Name",
            value=student.get("First_Name", ""),
            key=f"first_name_{key_suffix}"
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female"],
            index=0 if student.get("Gender", "Male") == "Male" else 1,
            key=f"gender_{key_suffix}"
        )

        student_class = st.selectbox(
            "Class",
            [str(i) for i in range(1, 13)],
            index=max(int(student.get("Class", "1")) - 1, 0),
            key=f"class_{key_suffix}"
        )

        date_of_birth = st.date_input(
            "Date of Birth",
            value=_parse_date(student.get("Date_of_Birth"), date(2015, 1, 1)),
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            key=f"dob_{key_suffix}"
        )

    with col2:
        last_name = st.text_input(
            "Last Name",
            value=student.get("Last_Name", ""),
            key=f"last_name_{key_suffix}"
        )

        section = st.selectbox(
            "Section",
            ["A", "B", "C"],
            index=["A", "B", "C"].index(student.get("Section", "A")),
            key=f"section_{key_suffix}"
        )

        parent_mobile = st.text_input(
            "Parent Mobile",
            value=student.get("Parent_Mobile", ""),
            key=f"parent_mobile_{key_suffix}"
        )

        status = st.selectbox(
            "Status",
            ["Active", "Inactive"],
            index=0 if student.get("Status", "Active") == "Active" else 1,
            key=f"status_{key_suffix}"
        )

        blood_group_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
        blood_group = st.selectbox(
            "Blood Group",
            blood_group_options,
            index=blood_group_options.index(student.get("Blood_Group") or "Unknown"),
            key=f"blood_group_{key_suffix}"
        )

    st.divider()
    st.caption("Parent & Contact Details")

    col3, col4 = st.columns(2)

    with col3:
        father_name = st.text_input(
            "Father's Name",
            value=student.get("Father_Name", ""),
            key=f"father_name_{key_suffix}"
        )

        email = st.text_input(
            "Email",
            value=student.get("Email", ""),
            key=f"email_{key_suffix}"
        )

        city = st.text_input(
            "City",
            value=student.get("City", ""),
            key=f"city_{key_suffix}"
        )

    with col4:
        mother_name = st.text_input(
            "Mother's Name",
            value=student.get("Mother_Name", ""),
            key=f"mother_name_{key_suffix}"
        )

        state = st.text_input(
            "State",
            value=student.get("State", ""),
            key=f"state_{key_suffix}"
        )

        house_options = ["Red", "Blue", "Green", "Yellow"]
        house = st.selectbox(
            "House",
            house_options,
            index=house_options.index(student.get("House") or "Yellow"),
            key=f"house_{key_suffix}"
        )

        fee_category_options = ["General", "Scholarship", "Sibling"]
        fee_category = st.selectbox(
            "Fee Category",
            fee_category_options,
            index=fee_category_options.index(student.get("Fee_Category") or "General"),
            key=f"fee_category_{key_suffix}"
        )

    return {
        "Admission_No": admission_no,
        "Roll_No": roll_no,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Gender": gender,
        "Class": student_class,
        "Section": section,
        "Parent_Mobile": parent_mobile,
        "Status": status,
        "Date_of_Birth": date_of_birth,
        "Blood_Group": None if blood_group == "Unknown" else blood_group,
        "Father_Name": father_name,
        "Mother_Name": mother_name,
        "Email": email,
        "City": city,
        "State": state,
        "House": house,
        "Fee_Category": fee_category,
    }