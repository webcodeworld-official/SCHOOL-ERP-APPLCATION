import streamlit as st
from database.transportation_queries import (
    add_transportation_record, update_transportation_record, delete_transportation_record,
    get_distinct_routes, get_unassigned_students, get_transportation_dict,
    sync_student_transport_id, clear_student_transport_id
)
from components.transportation_form import transportation_form


@st.dialog("🚌 Assign Transport")
def assign_transport_dialog():
    routes_df = get_distinct_routes()
    unassigned_df = get_unassigned_students()

    data = transportation_form(routes_df=routes_df, unassigned_df=unassigned_df)

    if st.button("Assign", use_container_width=True):

        if data["Student_ID"] is None:
            st.error("No student selected — nothing to assign.")
            return

        if not data["Route"]:
            st.error("Route name is required.")
            return

        values = (
            data["Transport_ID"],
            data["Student_ID"],
            data["Bus_No"],
            data["Route"],
            data["Pickup_Point"],
            data["Driver"],
            data["Driver_Phone"],
            data["Distance_KM"],
            data["Transport_Fee"],
        )

        add_transportation_record(values)
        sync_student_transport_id(data["Student_ID"], data["Transport_ID"])
        st.success("Transport assigned successfully.")
        st.rerun()


@st.dialog("✏️ Edit Assignment")
def edit_transportation_dialog(selected_record):
    student_id = int(selected_record["Student_ID"])
    full_record = get_transportation_dict(student_id)
    routes_df = get_distinct_routes()

    data = transportation_form(full_record, routes_df=routes_df)

    if st.button("Update", use_container_width=True):

        values = (
            data["Transport_ID"],
            data["Bus_No"],
            data["Route"],
            data["Pickup_Point"],
            data["Driver"],
            data["Driver_Phone"],
            data["Distance_KM"],
            data["Transport_Fee"],
            student_id,
        )

        update_transportation_record(values)
        sync_student_transport_id(student_id, data["Transport_ID"])
        st.success("Assignment updated successfully.")
        st.rerun()


@st.dialog("🗑 Remove Assignment")
def delete_transportation_dialog(selected_record):
    st.warning(
        f"Remove transport assignment for Student ID **{selected_record['Student_ID']}** "
        f"(Bus {selected_record['Bus_No']})? This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Remove", use_container_width=True):
            student_id = int(selected_record["Student_ID"])
            delete_transportation_record(student_id)
            clear_student_transport_id(student_id)
            st.success("Assignment removed.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
