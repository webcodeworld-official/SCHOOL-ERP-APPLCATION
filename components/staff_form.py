import streamlit as st
from datetime import date, datetime


def _parse_date(value, default):
    if not value:
        return default
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return default


def staff_form(staff=None):
    """
    Reusable Staff Form.

    If staff=None -> Add Staff
    If staff has data -> Edit Staff

    Returns dictionary containing all entered values.
    """

    if staff is None:
        staff = {}

    key_suffix = str(staff.get("Staff_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        staff_id = st.text_input(
            "Staff ID",
            value=str(staff.get("Staff_ID", "")),
            disabled=True,
            key=f"staff_id_{key_suffix}"
        )

        employee_name = st.text_input(
            "Employee Name",
            value=staff.get("Employee_Name", ""),
            key=f"employee_name_{key_suffix}"
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female"],
            index=0 if staff.get("Gender", "Male") == "Male" else 1,
            key=f"gender_{key_suffix}"
        )

        department_options = ["Accounts", "Admin", "English", "Library", "Math", "Science", "Sports"]
        department = st.selectbox(
            "Department",
            department_options,
            index=department_options.index(staff.get("Department", "Admin")),
            key=f"department_{key_suffix}"
        )

        designation_options = ["Clerk", "Coach", "Librarian", "Principal", "Senior Teacher", "Teacher"]
        designation = st.selectbox(
            "Designation",
            designation_options,
            index=designation_options.index(staff.get("Designation", "Teacher")),
            key=f"designation_{key_suffix}"
        )

    with col2:
        qualification_options = ["B.Ed", "M.Ed", "M.Sc", "MBA"]
        qualification = st.selectbox(
            "Qualification",
            qualification_options,
            index=qualification_options.index(staff.get("Qualification", "B.Ed")),
            key=f"qualification_{key_suffix}"
        )

        experience_yrs = st.number_input(
            "Experience (Years)",
            min_value=0,
            max_value=50,
            value=int(staff.get("Experience_Yrs", 0)),
            key=f"experience_{key_suffix}"
        )

        joining_date = st.date_input(
            "Joining Date",
            value=_parse_date(staff.get("Joining_Date"), date.today()),
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            disabled=staff.get("Staff_ID") is not None,  # locked once set (Edit mode)
            key=f"joining_date_{key_suffix}"
        )

        salary = st.number_input(
            "Salary",
            min_value=0,
            value=int(staff.get("Salary", 0)),
            step=1000,
            key=f"salary_{key_suffix}"
        )

        status = st.selectbox(
            "Status",
            ["Active", "Inactive"],
            index=0 if staff.get("Status", "Active") == "Active" else 1,
            key=f"status_{key_suffix}"
        )

    st.divider()
    st.caption("Contact Details")

    col3, col4 = st.columns(2)

    with col3:
        phone = st.text_input(
            "Phone",
            value=staff.get("Phone", ""),
            key=f"phone_{key_suffix}"
        )

    with col4:
        email = st.text_input(
            "Email",
            value=staff.get("Email", ""),
            key=f"email_{key_suffix}"
        )

    return {
        "Employee_Name": employee_name,
        "Gender": gender,
        "Department": department,
        "Designation": designation,
        "Qualification": qualification,
        "Experience_Yrs": experience_yrs,
        "Joining_Date": joining_date,
        "Salary": salary,
        "Phone": phone,
        "Email": email,
        "Status": status,
    }