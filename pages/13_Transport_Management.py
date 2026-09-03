import io
import streamlit as st
from database.transportation_queries import get_all_transportation
from components.transportation_cards import show_transportation_cards
from components.transportation_table import show_transportation_table
from components.transportation_dialogs import (
    assign_transport_dialog,
    edit_transportation_dialog,
    delete_transportation_dialog
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

records = get_all_transportation(branch_id=st.session_state.get("active_branch_id"))

from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

st.title("🚌 Transport Management")
st.caption("Manage student bus route assignments.")
st.divider()

show_transportation_cards(records)

st.divider()

col_search, col_route, col_sort, col_order = st.columns([2, 1, 1, 0.7])

with col_search:
    search = st.text_input(
        "🔍 Search",
        placeholder="Search by Student ID, Bus No, Driver..."
    )

with col_route:
    route_options = ["All"] + sorted(records["Route"].dropna().unique().tolist())
    selected_route = st.selectbox("Route", route_options)

with col_sort:
    sort_by = st.selectbox("Sort by", ["Student_ID", "Bus_No", "Transport_Fee", "Distance_KM"])

with col_order:
    st.write("")
    descending = st.toggle("⬇️ Desc")

filtered_records = records.copy()

if search:
    filtered_records = filtered_records[
        filtered_records["Student_ID"].astype(str).str.contains(search, case=False, na=False)
        | filtered_records["Bus_No"].astype(str).str.contains(search, case=False, na=False)
        | filtered_records["Driver"].astype(str).str.contains(search, case=False, na=False)
    ]

if selected_route != "All":
    filtered_records = filtered_records[filtered_records["Route"] == selected_route]

filtered_records = filtered_records.sort_values(by=sort_by, ascending=not descending)

st.caption(f"Showing {len(filtered_records)} assignment(s)")

selected_record = show_transportation_table(filtered_records)

if selected_record is None or (hasattr(selected_record, "__len__") and len(selected_record) == 0):
    selected_record = []

st.divider()

btn1, btn2, btn3, btn4 = st.columns([1.2, 1.2, 1.2, 1.2])

with btn1:
    if st.button("🚌 Assign Transport", use_container_width=True):
        assign_transport_dialog()

with btn2:
    if st.button("✏️ Edit", use_container_width=True, disabled=len(selected_record) == 0):
        edit_transportation_dialog(selected_record)

with btn3:
    if st.button("🗑 Remove", use_container_width=True, disabled=len(selected_record) == 0):
        delete_transportation_dialog(selected_record)

with btn4:
    with st.popover("📤 Export", use_container_width=True):
        st.caption(f"Exporting {len(filtered_records)} record(s)")

        excel_buffer = io.BytesIO()
        filtered_records.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        st.download_button(
            label="⬇️ Download as Excel (.xlsx)",
            data=excel_buffer,
            file_name="transportation_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        csv_data = filtered_records.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download as CSV",
            data=csv_data,
            file_name="transportation_export.csv",
            mime="text/csv",
            use_container_width=True
        )
