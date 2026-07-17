import streamlit as st
from datetime import date, datetime
from database.visitor_queries import (
    add_visitor, update_visitor, delete_visitor,
    get_next_visitor_id, generate_pass_no, get_visitor_dict
)
from components.visitor_form import visitor_form


@st.dialog("➕ Add Visitor")
def add_visitor_dialog():

    next_id = get_next_visitor_id()
    pass_no = generate_pass_no(next_id)
    preview = {"Visitor_ID": next_id, "Pass_No": pass_no}

    data = visitor_form(preview)

    if st.button("Save", use_container_width=True):

        if not data["Visitor_Name"]:
            st.error("Visitor Name is required.")
            return

        if data["Check_Out"] < data["Check_In"]:
            st.error("Check Out time cannot be before Check In time.")
            return

        values = (
            next_id,
            str(data["Visit_Date"]),
            data["Visitor_Name"],
            data["Visitor_Type"],
            data["Purpose"],
            data["Student_ID"] or None,
            data["Staff_Name"] or None,
            data["Check_In"].strftime("%H:%M"),
            data["Check_Out"].strftime("%H:%M"),
            pass_no,
        )

        add_visitor(values)
        st.success(f"Visitor logged successfully. Pass No: {pass_no}")
        st.rerun()


@st.dialog("✏️ Edit Visitor")
def edit_visitor_dialog(selected_visitor):
    visitor_id = int(selected_visitor["Visitor_ID"])
    full_visitor = get_visitor_dict(visitor_id)

    data = visitor_form(full_visitor)

    if st.button("Update", use_container_width=True):

        if not data["Visitor_Name"]:
            st.error("Visitor Name is required.")
            return

        if data["Check_Out"] < data["Check_In"]:
            st.error("Check Out time cannot be before Check In time.")
            return

        values = (
            str(data["Visit_Date"]),
            data["Visitor_Name"],
            data["Visitor_Type"],
            data["Purpose"],
            data["Student_ID"] or None,
            data["Staff_Name"] or None,
            data["Check_In"].strftime("%H:%M"),
            data["Check_Out"].strftime("%H:%M"),
            visitor_id,
        )

        update_visitor(values)
        st.success("Visitor record updated successfully.")
        st.rerun()


@st.dialog("🗑 Delete Visitor")
def delete_visitor_dialog(selected_visitor):
    st.warning(
        f"Are you sure you want to delete the visit record for "
        f"**{selected_visitor['Visitor_Name']}** (Pass No: {selected_visitor['Pass_No']})? "
        f"This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_visitor(int(selected_visitor["Visitor_ID"]))
            st.success("Visitor record deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()