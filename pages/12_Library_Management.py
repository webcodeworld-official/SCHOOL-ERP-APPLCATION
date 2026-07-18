import io
import streamlit as st
from datetime import date
from database.library_queries import get_all_library_records
from components.library_cards import show_library_cards
from components.library_table import show_library_table
from components.library_dialogs import (
    issue_book_dialog,
    edit_library_dialog,
    return_book_dialog,
    delete_library_dialog
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

records = get_all_library_records()

st.title("📚 Library Management")
st.caption("Manage book issues, returns, and overdue fines.")
st.divider()

show_library_cards(records)

st.divider()

# --------------------------------------------------
# SEARCH & FILTERS
# --------------------------------------------------

col_search, col_status, col_sort, col_order = st.columns([2, 1, 1, 0.7])

with col_search:
    search = st.text_input(
        "🔍 Search",
        placeholder="Search by Student ID, Book Name..."
    )

with col_status:
    status_options = ["All", "Issued", "Returned", "Overdue"]
    selected_status = st.selectbox("Status", status_options)

with col_sort:
    sort_by = st.selectbox("Sort by", ["Issue_Date", "Due_Date", "Student_ID"])

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc", value=True)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_records = records.copy()

if search:
    filtered_records = filtered_records[
        filtered_records["Student_ID"].astype(str).str.contains(search, case=False, na=False)
        | filtered_records["Book_Name"].astype(str).str.contains(search, case=False, na=False)
    ]

today = date.today()

if selected_status == "Issued":
    filtered_records = filtered_records[
        filtered_records["Return_Date"].isna()
        & (filtered_records["Due_Date"].apply(lambda d: date.fromisoformat(str(d)) >= today))
    ]
elif selected_status == "Returned":
    filtered_records = filtered_records[filtered_records["Return_Date"].notna()]
elif selected_status == "Overdue":
    filtered_records = filtered_records[
        filtered_records["Return_Date"].isna()
        & (filtered_records["Due_Date"].apply(lambda d: date.fromisoformat(str(d)) < today))
    ]

filtered_records = filtered_records.sort_values(by=sort_by, ascending=not descending)

# --------------------------------------------------
# TABLE
# --------------------------------------------------

st.caption(f"Showing {len(filtered_records)} record(s)")

selected_record = show_library_table(filtered_records)

if selected_record is None or (hasattr(selected_record, "__len__") and len(selected_record) == 0):
    selected_record = []

st.divider()

# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

btn1, btn2, btn3, btn4, btn5 = st.columns([1, 1, 1, 1, 1])

with btn1:
    if st.button("📕 Issue Book", use_container_width=True):
        issue_book_dialog()

with btn2:
    already_returned = len(selected_record) > 0 and selected_record.get("Return_Date") is not None
    if st.button(
        "📗 Return",
        use_container_width=True,
        disabled=len(selected_record) == 0 or already_returned
    ):
        return_book_dialog(selected_record)

with btn3:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_record) == 0):
        edit_library_dialog(selected_record)

with btn4:
    if st.button("🗑 Delete", use_container_width=True, disabled=len(selected_record) == 0):
        delete_library_dialog(selected_record)

with btn5:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_records)} record(s)")

        excel_buffer = io.BytesIO()
        filtered_records.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="library_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_records.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="library_export.csv",
            mime="text/csv",
            use_container_width=True
        )
