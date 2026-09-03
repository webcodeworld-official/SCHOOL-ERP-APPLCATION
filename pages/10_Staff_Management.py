import io
import streamlit as st
from database.staff_queries import get_all_staff
from components.staff_cards import show_staff_cards
from components.staff_table import show_staff_table
from components.staff_dialogs import (
    add_staff_dialog,
    edit_staff_dialog,
    delete_staff_dialog
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

staff = get_all_staff(branch_id=st.session_state.get("active_branch_id"))

from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("👩‍🏫 Staff Management")
st.caption("Manage all staff records from the database.")
st.divider()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

show_staff_cards(staff)

st.divider()

# --------------------------------------------------
# SEARCH & FILTERS
# --------------------------------------------------

col_search, col_dept, col_desig, col_sort, col_order = st.columns([2, 1, 1, 1, 0.7])

with col_search:
    search = st.text_input(
        "🔍 Search Staff",
        placeholder="Search by Staff ID, Name, Phone or Email..."
    )

with col_dept:
    dept_options = ["All"] + sorted(staff["Department"].dropna().unique().tolist())
    selected_dept = st.selectbox("Department", dept_options)

with col_desig:
    desig_options = ["All"] + sorted(staff["Designation"].dropna().unique().tolist())
    selected_desig = st.selectbox("Designation", desig_options)

with col_sort:
    sort_by = st.selectbox(
        "Sort by",
        ["Employee_Name", "Department", "Designation", "Joining_Date", "Salary"]
    )

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc")

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_staff = staff.copy()

if search:
    filtered_staff = filtered_staff[
        filtered_staff["Staff_ID"].astype(str).str.contains(search, case=False, na=False)
        | filtered_staff["Employee_Name"].str.contains(search, case=False, na=False)
        | filtered_staff["Phone"].astype(str).str.contains(search, case=False, na=False)
        | filtered_staff["Email"].astype(str).str.contains(search, case=False, na=False)
    ]

if selected_dept != "All":
    filtered_staff = filtered_staff[filtered_staff["Department"] == selected_dept]

if selected_desig != "All":
    filtered_staff = filtered_staff[filtered_staff["Designation"] == selected_desig]

filtered_staff = filtered_staff.sort_values(by=sort_by, ascending=not descending)

# --------------------------------------------------
# STAFF TABLE
# --------------------------------------------------

st.caption(f"Showing {len(filtered_staff)} staff member(s)")

selected_staff = show_staff_table(filtered_staff)

if selected_staff is None or (hasattr(selected_staff, "__len__") and len(selected_staff) == 0):
    selected_staff = []

st.divider()

# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

btn1, btn2, btn3, btn4 = st.columns([1.2, 1.2, 1.2, 1.2])

with btn1:
    if st.button("➕ Add Staff", use_container_width=True):
        add_staff_dialog()

with btn2:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_staff) == 0):
        edit_staff_dialog(selected_staff)

with btn3:
    if st.button("🗑 Delete", use_container_width=True, disabled=len(selected_staff) == 0):
        delete_staff_dialog(selected_staff)

with btn4:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_staff)} staff member(s)")

        excel_buffer = io.BytesIO()
        filtered_staff.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="staff_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_staff.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="staff_export.csv",
            mime="text/csv",
            use_container_width=True
        )