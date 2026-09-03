import streamlit as st
from datetime import date
from database.leave_queries import (
    LEAVE_TYPES, get_staff_by_id, submit_leave_request,
    get_all_leave_requests, review_leave_request, delete_leave_request
)
from database.branch_queries import get_branch_name
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

active_branch_id = st.session_state.get("active_branch_id")
role = st.session_state.get("role")

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">ERP Management</div>
    <div class="erp-title">🗓️ Leave Management</div>
    <div class="erp-subtitle">Submit and review staff leave requests.</div>
</div>
""", unsafe_allow_html=True)

st.caption(f"🏢 Viewing: **{get_branch_name(active_branch_id)}**")

tab_submit, tab_review = st.tabs(["📝 Submit Leave Request", "✅ Review Requests"])

with tab_submit:
    st.caption("Select your Department, Designation, and Name to submit a leave request.")

    from database.leave_queries import (
        get_staff_departments, get_designations_for_department, get_staff_for_dept_designation
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        departments = get_staff_departments(branch_id=active_branch_id)
        selected_dept = st.selectbox("Department", departments, key="submit_dept") if departments else None

    matched_staff = None

    if selected_dept:
        with col_b:
            designations = get_designations_for_department(selected_dept, branch_id=active_branch_id)
            selected_designation = st.selectbox("Designation", designations, key="submit_designation") if designations else None

        if selected_designation:
            with col_c:
                staff_options_df = get_staff_for_dept_designation(selected_dept, selected_designation, branch_id=active_branch_id)
                if not staff_options_df.empty:
                    staff_labels = staff_options_df.apply(
                        lambda r: f"{r['Employee_Name']} ({r['Staff_ID']})", axis=1
                    ).tolist()
                    selected_staff_label = st.selectbox("Your Name", staff_labels, key="submit_staff_pick")
                    selected_staff_id = selected_staff_label.split("(")[-1].rstrip(")")
                    matched_staff = get_staff_by_id(selected_staff_id)
    if matched_staff and matched_staff["Status"] == "Active":
        leave_type = st.selectbox("Leave Type", LEAVE_TYPES, key="submit_leave_type")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today(), key="submit_start_date")
        with col2:
            end_date = st.date_input("End Date", value=date.today(), key="submit_end_date")

        reason = st.text_area("Reason", placeholder="Brief reason for leave", key="submit_reason")

        if st.button("Submit Request", use_container_width=True):
            if end_date < start_date:
                st.error("End Date cannot be before Start Date.")
            elif not reason:
                st.error("Please provide a reason.")
            else:
                leave_id = submit_leave_request(
                    matched_staff["Staff_ID"], leave_type,
                    start_date.isoformat(), end_date.isoformat(),
                    reason, matched_staff["Branch_ID"]
                )
                st.success(f"Leave request submitted (Request ID: {leave_id}). Awaiting approval.")
                st.rerun()

with tab_review:
    if role != "Admin":
        st.warning("Only Admin can review and approve leave requests.")
    else:
        requests_df = get_all_leave_requests(branch_id=active_branch_id)

        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"], key="review_status_filter")

        filtered = requests_df.copy()
        if status_filter != "All":
            filtered = filtered[filtered["Status"] == status_filter]

        st.caption(f"Showing {len(filtered)} request(s)")

        if filtered.empty:
            st.info("No leave requests to show.")
        else:
            for _, row in filtered.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="kpi-card" style="margin-bottom: 0.7rem;">
                        <strong>{row['Employee_Name']}</strong> ({row['Department']}) — {row['Leave_Type']}<br>
                        <span style="color:#A1A1AA; font-size:0.85rem;">
                            {row['Start_Date']} to {row['End_Date']} · Status: <strong>{row['Status']}</strong>
                        </span><br>
                        <span style="font-size:0.85rem;">Reason: {row['Reason']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if row["Status"] == "Pending":
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("✅ Approve", key=f"approve_{row['Leave_ID']}", use_container_width=True):
                                review_leave_request(
                                    row["Leave_ID"], "Approved",
                                    st.session_state.get("username"), ""
                                )
                                st.rerun()
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{row['Leave_ID']}", use_container_width=True):
                                review_leave_request(
                                    row["Leave_ID"], "Rejected",
                                    st.session_state.get("username"), ""
                                )
                                st.rerun()
                    else:
                        if st.button("🗑 Delete Record", key=f"delete_{row['Leave_ID']}"):
                            delete_leave_request(row["Leave_ID"])
                            st.rerun()
