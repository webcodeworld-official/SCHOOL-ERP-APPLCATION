import streamlit as st
from datetime import date
from database.staff_queries import (
    add_staff, update_staff, delete_staff,
    get_next_staff_id, phone_exists, email_exists,
    get_staff_dict
)
from components.staff_form import staff_form
from utils import is_valid_phone, is_valid_email


@st.dialog("➕ Add Staff")
def add_staff_dialog():

    next_id = get_next_staff_id()
    preview = {"Staff_ID": next_id}

    data = staff_form(preview)

    active_branch_id = st.session_state.get("active_branch_id")
    if active_branch_id is None:
        from database.branch_queries import get_all_branches
        branches = get_all_branches()
        if branches.empty:
            st.error("No branches exist yet. Add a branch first (Settings).")
            branch_id_for_new_staff = None
        else:
            branch_choice = st.selectbox(
                "Assign to Branch", branches["Branch_Name"].tolist(), key="add_staff_branch_pick"
            )
            branch_id_for_new_staff = int(
                branches[branches["Branch_Name"] == branch_choice]["Branch_ID"].iloc[0]
            )
    else:
        branch_id_for_new_staff = active_branch_id

    if st.button("Save", use_container_width=True):

        if not data["Employee_Name"]:
            st.error("Employee Name is required.")
            return

        if not is_valid_phone(data["Phone"]):
            st.error("Enter a valid 10-digit mobile number (starting 6-9).")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if phone_exists(data["Phone"]):
            st.warning("⚠️ This phone number is already used by another staff member.")

        if data["Email"] and email_exists(data["Email"]):
            st.warning("⚠️ This email is already used by another staff member.")

        
        values = (
            next_id,
            data["Employee_Name"],
            data["Gender"],
            data["Department"],
            data["Designation"],
            data["Qualification"],
            data["Experience_Yrs"],
            str(date.today()),  # Joining_Date — set once, at creation
            data["Salary"],
            data["Phone"],
            data["Email"],
            data["Status"],
            branch_id_for_new_staff,
        )

        add_staff(values)
        st.success(f"Staff added successfully. Staff ID: {next_id}")
        st.rerun()


@st.dialog("✏️ Edit Staff")
def edit_staff_dialog(selected_staff):
    staff_id = selected_staff["Staff_ID"]
    full_staff = get_staff_dict(staff_id)

    data = staff_form(full_staff)

    if st.button("Update", use_container_width=True):

        if not data["Employee_Name"]:
            st.error("Employee Name is required.")
            return

        if not is_valid_phone(data["Phone"]):
            st.error("Enter a valid 10-digit mobile number (starting 6-9).")
            return

        if data["Email"] and not is_valid_email(data["Email"]):
            st.error("Enter a valid email address.")
            return

        if phone_exists(data["Phone"], exclude_staff_id=staff_id):
            st.warning("⚠️ This phone number is already used by another staff member.")

        if data["Email"] and email_exists(data["Email"], exclude_staff_id=staff_id):
            st.warning("⚠️ This email is already used by another staff member.")

        values = (
            data["Employee_Name"],
            data["Gender"],
            data["Department"],
            data["Designation"],
            data["Qualification"],
            data["Experience_Yrs"],
            data["Salary"],
            data["Phone"],
            data["Email"],
            data["Status"],
            staff_id,
        )

        update_staff(values)
        st.success("Staff updated successfully.")
        st.rerun()


@st.dialog("🗑 Delete Staff")
def delete_staff_dialog(selected_staff):
    st.warning(
        f"Are you sure you want to delete **{selected_staff['Employee_Name']}** "
        f"(Staff ID: {selected_staff['Staff_ID']})? This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_staff(selected_staff["Staff_ID"])
            st.success("Staff deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()