import streamlit as st
from datetime import date, datetime, time
from database.visitor_queries import get_active_staff_for_meeting


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

    Returns dictionary containing all entered values, including Staff_ID
    for who they're meeting (a real link, not free text).
    """

    if visitor is None:
        visitor = {}

    key_suffix = str(visitor.get("Visitor_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        visitor_id = st.text_input(
            "Visitor ID", value=str(visitor.get("Visitor_ID", "")),
            disabled=True, key=f"visitor_id_{key_suffix}"
        )
        pass_no = st.text_input(
            "Pass No", value=str(visitor.get("Pass_No", "")),
            disabled=True, key=f"pass_no_{key_suffix}"
        )
        visitor_name = st.text_input(
            "Visitor Name", value=visitor.get("Visitor_Name", ""),
            key=f"visitor_name_{key_suffix}"
        )
        visitor_type_options = ["Guest", "Parent", "Vendor"]
        visitor_type = st.selectbox(
            "Visitor Type", visitor_type_options,
            index=visitor_type_options.index(visitor.get("Visitor_Type", "Guest")),
            key=f"visitor_type_{key_suffix}"
        )
        purpose_options = ["Admission Inquiry", "Delivery", "Meeting", "Parent Meeting", "Vendor"]
        purpose = st.selectbox(
            "Purpose", purpose_options,
            index=purpose_options.index(visitor.get("Purpose", "Meeting")),
            key=f"purpose_{key_suffix}"
        )

    with col2:
        visit_date = st.date_input(
            "Visit Date",
            value=datetime.strptime(str(visitor.get("Visit_Date")), "%Y-%m-%d").date()
                  if visitor.get("Visit_Date") else date.today(),
            max_value=date.today(), key=f"visit_date_{key_suffix}"
        )

        student_id = st.text_input(
            "Student ID (who they're visiting, if applicable)",
            value=str(visitor.get("Student_ID") or ""),
            key=f"student_id_{key_suffix}"
        )

        # --- Real "Meeting With" dropdown, tied to actual staff records ---
        staff_df = get_active_staff_for_meeting(branch_id=st.session_state.get("active_branch_id"))
        staff_options = staff_df.apply(
            lambda r: f"{r['Staff_ID']} - {r['Employee_Name']} ({r['Designation']})", axis=1
        ).tolist()

        current_staff_id = visitor.get("Staff_ID")
        default_index = 0
        if current_staff_id:
            for i, sid in enumerate(staff_df["Staff_ID"]):
                if sid == current_staff_id:
                    default_index = i
                    break

        selected_staff_label = st.selectbox(
            "Meeting With (Staff)", staff_options,
            index=default_index if staff_options else 0,
            key=f"meeting_with_{key_suffix}"
        )
        meeting_staff_id = selected_staff_label.split(" - ")[0] if staff_options else None

        check_in = st.time_input(
            "Check In",
            value=_parse_time(visitor.get("Check_In"), datetime.now().time()),
            disabled=visitor.get("Visitor_ID") is None,
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
        "Student_ID": student_id or None,
        "Staff_ID": meeting_staff_id,
        "Check_In": check_in,
        "Check_Out": check_out,
    }
