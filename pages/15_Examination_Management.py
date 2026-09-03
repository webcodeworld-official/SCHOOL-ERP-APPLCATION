import io
import streamlit as st
import pandas as pd
from database.examination_queries import (
    EXAM_NAMES, SUBJECTS, get_students_by_class_section,
    get_existing_marks, upsert_marks, get_all_results, delete_result
)
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

st.title("📝 Examination Management")
st.caption("Enter marks in bulk for a class, or manage individual results.")
st.divider()
from database.branch_queries import get_branch_name
current_branch_label = get_branch_name(st.session_state.get("active_branch_id"))
st.caption(f"🏢 Viewing: **{current_branch_label}**")

tab_entry, tab_manage = st.tabs(["📋 Bulk Marks Entry", "🔍 Manage Results"])

# ==================================================================
# TAB 1: BULK MARKS ENTRY
# ==================================================================
with tab_entry:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        exam_name = st.selectbox("Exam", EXAM_NAMES)

    with col2:
        subject = st.selectbox("Subject", SUBJECTS)

    with col3:
        class_selected = st.selectbox("Class", [str(i) for i in range(1, 13)])

    with col4:
        section_selected = st.selectbox("Section", ["A", "B", "C"])

    students = get_students_by_class_section(
    class_selected, section_selected,
    branch_id=st.session_state.get("active_branch_id")
)

    if students.empty:
        st.warning("No active students found for this Class + Section.")
    else:
        student_ids = students["Student_ID"].tolist()
        existing = get_existing_marks(exam_name, subject, student_ids)

        # Build the editable grid: one row per student, pre-filled with existing marks if any
        grid_rows = []
        for _, s in students.iterrows():
            sid = s["Student_ID"]
            existing_row = existing.get(sid)
            grid_rows.append({
                "Student_ID": sid,
                "Roll_No": s["Roll_No"],
                "Name": f"{s['First_Name']} {s['Last_Name']}",
                "Marks_Obtained": int(existing_row["Marks_Obtained"]) if existing_row is not None else 0,
                "Total_Marks": int(existing_row["Total_Marks"]) if existing_row is not None else 100,
            })

        grid_df = pd.DataFrame(grid_rows)

        st.caption(f"Entering marks for **{exam_name} — {subject} — Class {class_selected}{section_selected}** "
                   f"({len(grid_df)} students)")

        edited_df = st.data_editor(
            grid_df,
            column_config={
                "Student_ID": st.column_config.NumberColumn("Student ID", disabled=True),
                "Roll_No": st.column_config.TextColumn("Roll No", disabled=True),
                "Name": st.column_config.TextColumn("Name", disabled=True),
                "Marks_Obtained": st.column_config.NumberColumn("Marks Obtained", min_value=0, max_value=1000),
                "Total_Marks": st.column_config.NumberColumn("Total Marks", min_value=1, max_value=1000),
            },
            hide_index=True,
            use_container_width=True,
            key=f"marks_grid_{exam_name}_{subject}_{class_selected}_{section_selected}"
        )

        if st.button("💾 Save Marks", use_container_width=True):
            invalid = edited_df[edited_df["Marks_Obtained"] > edited_df["Total_Marks"]]
            if not invalid.empty:
                st.error(f"{len(invalid)} student(s) have Marks Obtained greater than Total Marks. Fix before saving.")
            else:
                entries = edited_df[["Student_ID", "Marks_Obtained", "Total_Marks"]].to_dict("records")
                upsert_marks(exam_name, subject, entries)
                st.success(f"Marks saved for {len(entries)} student(s).")
                st.rerun()

# ==================================================================
# TAB 2: MANAGE RESULTS (browse, filter, delete, export)
# ==================================================================
with tab_manage:

    results = get_all_results(branch_id=st.session_state.get("active_branch_id"))

    col_search, col_exam, col_subject, col_result = st.columns(4)

    with col_search:
        search = st.text_input("🔍 Search Student ID")

    with col_exam:
        exam_filter = st.selectbox("Exam", ["All"] + EXAM_NAMES, key="manage_exam")

    with col_subject:
        subject_filter = st.selectbox("Subject", ["All"] + SUBJECTS, key="manage_subject")

    with col_result:
        result_filter = st.selectbox("Result", ["All", "Pass", "Fail"], key="manage_result")

    filtered = results.copy()

    if search:
        filtered = filtered[filtered["Student_ID"].astype(str).str.contains(search, na=False)]

    if exam_filter != "All":
        filtered = filtered[filtered["Exam_Name"] == exam_filter]

    if subject_filter != "All":
        filtered = filtered[filtered["Subject"] == subject_filter]

    if result_filter != "All":
        filtered = filtered[filtered["Result"] == result_filter]

    st.caption(f"Showing {len(filtered)} result(s)")

    selected = st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    selected_row = None
    if selected.selection.rows:
        selected_row = filtered.iloc[selected.selection.rows[0]]

    st.divider()

    btn1, btn2 = st.columns([1, 1])

    with btn1:
        if st.button("🗑 Delete Selected", use_container_width=True, disabled=selected_row is None):
            delete_result(selected_row["Result_ID"])
            st.success("Result deleted.")
            st.rerun()

    with btn2:
        with st.popover("📤 Export", use_container_width=True):
            st.caption(f"Exporting {len(filtered)} result(s)")

            excel_buffer = io.BytesIO()
            filtered.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            st.download_button(
                label="⬇️ Download as Excel (.xlsx)",
                data=excel_buffer,
                file_name="examination_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            csv_data = filtered.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download as CSV",
                data=csv_data,
                file_name="examination_export.csv",
                mime="text/csv",
                use_container_width=True
            )
