import io
import streamlit as st
from database.fees_queries import get_all_fees, ACADEMIC_MONTHS
from components.fees_cards import show_fees_cards
from components.fees_table import show_fees_table
from components.fees_dialogs import (
    add_fee_dialog,
    edit_fee_dialog,
    record_payment_dialog,
    delete_fee_dialog
)
from utils import load_custom_css
load_custom_css()


records = get_all_fees()

st.title("💰 Fee Management")
st.caption("Manage student fee records and payments.")
st.divider()

show_fees_cards(records)

st.divider()

col_search, col_month, col_status, col_sort, col_order = st.columns([2, 1, 1, 1, 0.7])

with col_search:
    search = st.text_input("🔍 Search", placeholder="Search by Student ID...")

with col_month:
    month_options = ["All"] + ACADEMIC_MONTHS
    selected_month = st.selectbox("Month", month_options)

with col_status:
    status_options = ["All", "Paid", "Partial", "Pending"]
    selected_status = st.selectbox("Status", status_options)

with col_sort:
    sort_by = st.selectbox("Sort by", ["Student_ID", "Total_Fee", "Balance", "Month"])

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc")

filtered_records = records.copy()

if search:
    filtered_records = filtered_records[
        filtered_records["Student_ID"].astype(str).str.contains(search, case=False, na=False)
    ]

if selected_month != "All":
    filtered_records = filtered_records[filtered_records["Month"] == selected_month]

if selected_status != "All":
    filtered_records = filtered_records[filtered_records["Payment_Status"] == selected_status]

filtered_records = filtered_records.sort_values(by=sort_by, ascending=not descending)

st.caption(f"Showing {len(filtered_records)} record(s)")

selected_record = show_fees_table(filtered_records)

if selected_record is None or (hasattr(selected_record, "__len__") and len(selected_record) == 0):
    selected_record = []

st.divider()

btn1, btn2, btn3, btn4, btn5 = st.columns([1, 1, 1, 1, 1])

with btn1:
    if st.button("💰 Add Fee Record", use_container_width=True):
        add_fee_dialog()

with btn2:
    already_paid = len(selected_record) > 0 and selected_record.get("Payment_Status") == "Paid"
    if st.button(
        "💳 Record Payment",
        use_container_width=True,
        disabled=len(selected_record) == 0 or already_paid
    ):
        record_payment_dialog(selected_record)

with btn3:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_record) == 0):
        edit_fee_dialog(selected_record)

with btn4:
    if st.button("🗑 Delete", use_container_width=True, disabled=len(selected_record) == 0):
        delete_fee_dialog(selected_record)

with btn5:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_records)} record(s)")

        excel_buffer = io.BytesIO()
        filtered_records.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="fees_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_records.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="fees_export.csv",
            mime="text/csv",
            use_container_width=True
        )
