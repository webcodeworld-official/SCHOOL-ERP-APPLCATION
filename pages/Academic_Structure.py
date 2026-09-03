import streamlit as st
import pandas as pd
from datetime import date
from database.academic_queries import (
    get_all_subjects, get_curriculum_for_class, get_teacher_assignments,
    get_teachers_for_subject, update_teacher_assignment, get_timetable,
    OVERRIDE_TYPES, WHOLE_DAY_TYPES, add_override, get_overrides_for_class,
    delete_override, get_effective_schedule_for_date
)
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">ERP Management</div>
    <div class="erp-title">📖 Academic Structure</div>
    <div class="erp-subtitle">Subjects, curriculum, teacher assignments, and weekly timetables.</div>
</div>
""", unsafe_allow_html=True)

(tab_subjects, tab_curriculum, tab_assignments,
 tab_timetable, tab_by_date, tab_overrides) = st.tabs([
    "📚 Subjects", "🏫 Curriculum by Class", "👩‍🏫 Teacher Assignments",
    "🗓️ Master Timetable", "📅 View by Date", "⚠️ Manage Overrides"
])

# --------------------------------------------------
# TAB 1: SUBJECTS
# --------------------------------------------------
with tab_subjects:
    subjects = get_all_subjects()
    st.caption(f"{len(subjects)} subjects across the curriculum")
    st.dataframe(subjects, use_container_width=True, hide_index=True)

# --------------------------------------------------
# TAB 2: CURRICULUM BY CLASS
# --------------------------------------------------
with tab_curriculum:
    class_options = [str(i) for i in range(1, 13)]
    selected_class = st.selectbox("Select Class", class_options, key="curriculum_class")

    curriculum = get_curriculum_for_class(selected_class)
    st.caption(f"Class {selected_class} studies {len(curriculum)} subjects")
    st.dataframe(
        curriculum[["Subject_Name", "Subject_Code", "Type"]],
        use_container_width=True, hide_index=True
    )

# --------------------------------------------------
# TAB 3: TEACHER ASSIGNMENTS
# --------------------------------------------------
with tab_assignments:
    col1, col2 = st.columns(2)
    with col1:
        assign_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="assign_class")
    with col2:
        assign_section = st.selectbox("Section", ["A", "B", "C"], key="assign_section")

    assignments = get_teacher_assignments(assign_class, assign_section, branch_id=st.session_state.get("active_branch_id"))

    if assignments.empty:
        st.warning("No subjects/teachers found for this Class-Section.")
    else:
        st.caption(f"Teacher assignments for Class {assign_class} - Section {assign_section}")

        for _, row in assignments.iterrows():
            col_subj, col_teacher, col_action = st.columns([2, 3, 2])
            with col_subj:
                st.write(f"**{row['Subject_Name']}**")
            with col_teacher:
                st.write(row["Employee_Name"])
            with col_action:
                with st.popover("🔄 Reassign", use_container_width=True):
                    eligible = get_teachers_for_subject(row["Subject_Name"], branch_id=st.session_state.get("active_branch_id"))
                    if eligible.empty:
                        st.caption("No other eligible teachers found.")
                    else:
                        options = eligible.apply(
                            lambda r: f"{r['Staff_ID']} - {r['Employee_Name']}", axis=1
                        ).tolist()
                        choice = st.selectbox("New teacher", options, key=f"reassign_{row['Assignment_ID']}")
                        if st.button("Confirm", key=f"confirm_{row['Assignment_ID']}"):
                            new_staff_id = choice.split(" - ")[0]
                            update_teacher_assignment(row["Assignment_ID"], new_staff_id)
                            st.success("Teacher reassigned.")
                            st.rerun()

# --------------------------------------------------
# TAB 4: MASTER TIMETABLE (weekly recurring, now with Room)
# --------------------------------------------------
with tab_timetable:
    col1, col2 = st.columns(2)
    with col1:
        tt_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="tt_class")
    with col2:
        tt_section = st.selectbox("Section", ["A", "B", "C"], key="tt_section")

    timetable = get_timetable(tt_class, tt_section, branch_id=st.session_state.get("active_branch_id"))
    if timetable.empty:
        st.warning("No timetable found for this Class-Section.")
    else:
        timetable["Cell"] = timetable["Subject_Name"] + " (" + timetable["Room"] + ")"
        pivot = timetable.pivot_table(index="Period", columns="Day", values="Cell", aggfunc="first")

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        pivot = pivot.reindex(columns=[d for d in day_order if d in pivot.columns])

        st.caption(f"Weekly master timetable — Class {tt_class}, Section {tt_section} (Subject + Room)")
        st.dataframe(pivot, use_container_width=True)

# --------------------------------------------------
# TAB 5: VIEW BY DATE (master + overrides merged)
# --------------------------------------------------
with tab_by_date:
    col1, col2, col3 = st.columns(3)
    with col1:
        date_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="date_class")
    with col2:
        date_section = st.selectbox("Section", ["A", "B", "C"], key="date_section")
    with col3:
        selected_date = st.date_input("Select Date", value=date.today(), key="date_picker")

    schedule_df, whole_day_note = get_effective_schedule_for_date(
    date_class, date_section, selected_date,
    branch_id=st.session_state.get("active_branch_id")
)
    
    st.caption(f"Schedule for Class {date_class}-{date_section} on {selected_date.strftime('%A, %d %B %Y')}")

    if whole_day_note:
        st.info(f"📌 {whole_day_note}")
    elif schedule_df.empty:
        st.warning("No school / no timetable for this day.")
    else:
        def highlight_override(row):
            return ['background-color: rgba(251, 191, 36, 0.15)' if row["Note"] else '' for _ in row]

        st.dataframe(
            schedule_df.style.apply(highlight_override, axis=1),
            use_container_width=True, hide_index=True
        )
        if schedule_df["Note"].str.strip().any():
            st.caption("🟡 Highlighted rows have an override applied for this specific date.")

# --------------------------------------------------
# TAB 6: MANAGE OVERRIDES
# --------------------------------------------------
with tab_overrides:
    st.subheader("➕ Add a Schedule Override")

    col1, col2, col3 = st.columns(3)
    with col1:
        ov_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="ov_class")
    with col2:
        ov_section = st.selectbox("Section", ["A", "B", "C"], key="ov_section")
    with col3:
        ov_date = st.date_input("Date", value=date.today(), key="ov_date")

    ov_type = st.selectbox("Override Type", OVERRIDE_TYPES, key="ov_type")

    is_whole_day = ov_type in WHOLE_DAY_TYPES

    ov_period = None
    new_subject_id = None
    new_staff_id = None
    new_room = None

    if not is_whole_day:
        ov_period = st.selectbox("Period", list(range(1, 8)), key="ov_period")

        if ov_type == "Teacher Substitution":
            from database.connection import get_connection
            conn = get_connection()
            staff_df = pd.read_sql("SELECT Staff_ID, Employee_Name FROM staff WHERE Status='Active'", conn)
            conn.close()
            options = staff_df.apply(lambda r: f"{r['Staff_ID']} - {r['Employee_Name']}", axis=1).tolist()
            choice = st.selectbox("Substitute Teacher", options, key="ov_staff")
            new_staff_id = choice.split(" - ")[0]

        elif ov_type == "Room Change":
            new_room = st.text_input("New Room", key="ov_room")

        elif ov_type in ("Subject Replacement", "Extra Class", "Full-Day Replacement"):
            subjects_df = get_all_subjects()
            subj_options = subjects_df["Subject_Name"].tolist()
            chosen_subject = st.selectbox("New Subject", subj_options, key="ov_subject")
            new_subject_id = int(subjects_df[subjects_df["Subject_Name"] == chosen_subject]["Subject_ID"].iloc[0])

            eligible = get_teachers_for_subject(chosen_subject, branch_id=st.session_state.get("active_branch_id"))
            if not eligible.empty:
                t_options = eligible.apply(lambda r: f"{r['Staff_ID']} - {r['Employee_Name']}", axis=1).tolist()
                t_choice = st.selectbox("Teacher", t_options, key="ov_new_teacher")
                new_staff_id = t_choice.split(" - ")[0]

        elif ov_type == "Examination":
            subjects_df = get_all_subjects()
            subj_options = subjects_df["Subject_Name"].tolist()
            chosen_subject = st.selectbox("Subject Being Examined", subj_options, key="ov_exam_subject")
            new_subject_id = int(subjects_df[subjects_df["Subject_Name"] == chosen_subject]["Subject_ID"].iloc[0])

    remarks = st.text_area("Remarks / Reason", placeholder="e.g. Ms. Sharma on medical leave", key="ov_remarks")

    if st.button("Save Override", use_container_width=True):
       add_override(
         ov_class, ov_section, ov_date.isoformat(), ov_period, ov_type,
         new_subject_id, new_staff_id, new_room, remarks,
         st.session_state.get("active_branch_id")
    )
    st.success("Override saved.")
    st.rerun()

    st.divider()
    st.subheader("📋 Existing Overrides")

    existing = get_overrides_for_class(ov_class, ov_section, branch_id=st.session_state.get("active_branch_id"))
    if existing.empty:
        st.caption("No overrides recorded for this Class-Section yet.")
    else:
        st.dataframe(existing, use_container_width=True, hide_index=True)

        override_to_delete = st.selectbox(
            "Select an Override_ID to delete",
            existing["Override_ID"].tolist(),
            key="delete_override_select"
        )
        if st.button("🗑 Delete Selected Override", use_container_width=True):
            delete_override(override_to_delete)
            st.success("Override deleted.")
            st.rerun()
