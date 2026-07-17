import streamlit as st
from datetime import date, datetime, time


def _parse_time(value, default):
    if not value:
        return default
    if isinstance(value, time):
        return value
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except ValueError:
        return default


def visitor_form(visitor=None):
    """
    Reusable Visitor Form.

    If visitor=None -> Add Visitor (log a new visit)
    If visitor has data -> Edit Visitor

    Returns dictionary containing all entered values.
    """

    if visitor is None:
        visitor = {}

    key_suffix = str(visitor.get("Visitor_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        visitor_id = st.text_input(
            "Visitor ID",
            value=str(visitor.get("Visitor_ID", "")),
            disabled=True,
            key=f"visitor_id_{key_suffix}"
        )

        pass_no = st.text_input(
            "Pass No",
            value=str(visitor.get("Pass_No", "")),
            disabled=True,
            key=f"pass_no_{key_suffix}"
        )

        visitor_name = st.text_input(
            "Visitor Name",
            value=visitor.get("Visitor_Name", ""),
            key=f"visitor_name_{key_suffix}"
        )

        visitor_type_options = ["Guest", "Parent", "Vendor"]
        visitor_type = st.selectbox(
            "Visitor Type",
            visitor_type_options,
            index=visitor_type_options.index(visitor.get("Visitor_Type", "Guest")),
            key=f"visitor_type_{key_suffix}"
        )

        purpose_options = ["Admission Inquiry", "Delivery", "Meeting", "Parent Meeting", "Vendor"]
        purpose = st.selectbox(
            "Purpose",
            purpose_options,
            index=purpose_options.index(visitor.get("Purpose", "Meeting")),
            key=f"purpose_{key_suffix}"
        )

    with col2:
        visit_date = st.date_input(
            "Visit Date",
            value=_parse_time(None, date.today()) if not visitor.get("Visit_Date") else datetime.strptime(str(visitor.get("Visit_Date")), "%Y-%m-%d").date(),
            max_value=date.today(),
            key=f"visit_date_{key_suffix}"
        )

        student_id = st.text_input(
            "Student ID (who they're visiting)",
            value=str(visitor.get("Student_ID", "")),
            key=f"student_id_{key_suffix}"
        )

        staff_name = st.text_input(
            "Staff Name (who they're meeting)",
            value=str(visitor.get("Staff_Name", "")),
            key=f"staff_name_{key_suffix}"
        )

        check_in = st.time_input(
            "Check In",
            value=_parse_time(visitor.get("Check_In"), datetime.now().time()),
            disabled=visitor.get("Visitor_ID") is None,  # locked to "now" when adding
            key=f"check_in_{key_suffix}"
        )
        
        check_out = st.time_input(
            "Check Out",
            value=_parse_time(visitor.get("Check_Out"), datetime.now().time()),
            key=f"check_out_{key_suffix}"
        )

    return {
        "Visit_Date": visit_date,
        "Visitor_Name": visitor_name,
        "Visitor_Type": visitor_type,
        "Purpose": purpose,
        "Student_ID": student_id,
        "Staff_Name": staff_name,
        "Check_In": check_in,
        "Check_Out": check_out,
    }