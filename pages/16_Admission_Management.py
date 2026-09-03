import io
import streamlit as st
from database.admission_queries import get_all_admissions
from components.admission_cards import show_admission_cards
from components.admission_table import show_admission_table
from components.admission_dialogs import (
    add_admission_dialog,
    edit_admission_dialog,
    delete_admission_dialog
)
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

records = get_all_admissions(branch_id=st.session_state.get("active_branch_id"))

from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">ERP Management</div>
    <div class="erp-title">📥 Admission Management</div>
    <div class="erp-subtitle">Process and manage student admission records.</div>
</div>
""", unsafe_allow_html=True)

show_admission_cards(records)

st.divider()

col_search, col_status, col_sort, col_order = st.columns([2, 1, 1, 0.7])

with col_search:
    search = st.text_input("🔍 Search", placeholder="Search by Student ID...")

with col_status:
    status_options = ["All", "Approved", "Pending"]
    selected_status = st.selectbox("Status", status_options)

with col_sort:
    sort_by = st.selectbox("Sort by", ["Student_ID", "Admission_Date", "Admission_Fee"])

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc")

filtered_records = records.copy()

if search:
    filtered_records = filtered_records[
        filtered_records["Student_ID"].astype(str).str.contains(search, case=False, na=False)
    ]

if selected_status != "All":
    filtered_records = filtered_records[filtered_records["Admission_Status"] == selected_status]

filtered_records = filtered_records.sort_values(by=sort_by, ascending=not descending)

st.caption(f"Showing {len(filtered_records)} record(s)")

selected_record = show_admission_table(filtered_records)

if selected_record is None or (hasattr(selected_record, "__len__") and len(selected_record) == 0):
    selected_record = []

st.divider()

btn1, btn2, btn3, btn4 = st.columns([1.2, 1.2, 1.2, 1.2])

with btn1:
    if st.button("📥 Process Admission", use_container_width=True):
        add_admission_dialog()

with btn2:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_record) == 0):
        edit_admission_dialog(selected_record)

with btn3:
    if st.button("🗑 Delete", use_container_width=True, disabled=len(selected_record) == 0):
        delete_admission_dialog(selected_record)

with btn4:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_records)} record(s)")

        excel_buffer = io.BytesIO()
        filtered_records.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="admission_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_records.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="admission_export.csv",
            mime="text/csv",
            use_container_width=True
        )
