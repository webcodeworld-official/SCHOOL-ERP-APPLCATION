import io
import streamlit as st
from database.visitor_queries import get_all_visitors
from components.visitor_cards import show_visitor_cards
from components.visitor_table import show_visitor_table
from components.visitor_dialogs import (
    add_visitor_dialog,
    edit_visitor_dialog,
    delete_visitor_dialog
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

visitors = get_all_visitors(branch_id=st.session_state.get("active_branch_id"))

from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

st.title("🚶 Visitor Management")
st.caption("Manage all visitor logs from the database.")
st.divider()

show_visitor_cards(visitors)

st.divider()

col_search, col_type, col_purpose, col_sort, col_order = st.columns([2, 1, 1, 1, 0.7])

with col_search:
    search = st.text_input(
        "🔍 Search Visitor",
        placeholder="Search by Visitor ID, Pass No, or Name..."
    )

with col_type:
    type_options = ["All"] + sorted(visitors["Visitor_Type"].dropna().unique().tolist())
    selected_type = st.selectbox("Visitor Type", type_options)

with col_purpose:
    purpose_options = ["All"] + sorted(visitors["Purpose"].dropna().unique().tolist())
    selected_purpose = st.selectbox("Purpose", purpose_options)

with col_sort:
    sort_by = st.selectbox(
        "Sort by",
        ["Visit_Date", "Visitor_Name", "Check_In"]
    )

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc")

filtered_visitors = visitors.copy()

if search:
    filtered_visitors = filtered_visitors[
        filtered_visitors["Visitor_ID"].astype(str).str.contains(search, case=False, na=False)
        | filtered_visitors["Pass_No"].astype(str).str.contains(search, case=False, na=False)
        | filtered_visitors["Visitor_Name"].str.contains(search, case=False, na=False)
    ]

if selected_type != "All":
    filtered_visitors = filtered_visitors[filtered_visitors["Visitor_Type"] == selected_type]

if selected_purpose != "All":
    filtered_visitors = filtered_visitors[filtered_visitors["Purpose"] == selected_purpose]

filtered_visitors = filtered_visitors.sort_values(by=sort_by, ascending=not descending)

st.caption(f"Showing {len(filtered_visitors)} visitor record(s)")

selected_visitor = show_visitor_table(filtered_visitors)

if selected_visitor is None or (hasattr(selected_visitor, "__len__") and len(selected_visitor) == 0):
    selected_visitor = []

st.divider()

btn1, btn2, btn3, btn4 = st.columns([1.2, 1.2, 1.2, 1.2])

with btn1:
    if st.button("➕ Add Visitor", use_container_width=True):
        add_visitor_dialog()

with btn2:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_visitor) == 0):
        edit_visitor_dialog(selected_visitor)

with btn3:
    if st.button("🗑 Delete", use_container_width=True, disabled=len(selected_visitor) == 0):
        delete_visitor_dialog(selected_visitor)

with btn4:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_visitors)} visitor record(s)")

        excel_buffer = io.BytesIO()
        filtered_visitors.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="visitors_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_visitors.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="visitors_export.csv",
            mime="text/csv",
            use_container_width=True
        )