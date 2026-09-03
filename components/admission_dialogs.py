import streamlit as st
from datetime import date
from database.admission_queries import (
    add_admission_record, update_admission_record, delete_admission_record,
    get_students_without_admission_record, get_admission_dict
)
from components.admission_form import admission_form


@st.dialog("📥 Process Admission")
def add_admission_dialog():
    unassigned_df = get_students_without_admission_record(branch_id=st.session_state.get("active_branch_id"))
    data = admission_form(unassigned_df=unassigned_df)
    if st.button("Save", use_container_width=True):

        if data["Student_ID"] is None:
            st.error("No student selected.")
            return

        match = unassigned_df[unassigned_df["Student_ID"] == data["Student_ID"]].iloc[0]
        admission_date = str(match["Admission_Date"])
        admission_year = int(admission_date[:4])
        admission_id = f"ADM{data['Student_ID']}"
        student_branch_id = int(match["Branch_ID"])

        values = (
            admission_id,
            data["Student_ID"],
            admission_date,
            admission_year,
            data["Previous_School"],
            data["Admission_Status"],
            data["Entrance_Test"],
            data["Admission_Fee"],
            student_branch_id,
            data["Discount_Type"],
            data["Entrance_Test_Score"],
            data["Discount_Percentage"],
        )

        add_admission_record(values)

        from database.fee_structure_queries import auto_generate_yearly_fee_schedule
        months_created, fee_error = auto_generate_yearly_fee_schedule(
            data["Student_ID"], match["Class"], match.get("Stream"),
            str(admission_year) + "-" + str(admission_year + 1),
            student_branch_id, data["Discount_Percentage"],
            has_transport=bool(match.get("Transport_ID"))
        )

        if fee_error:
            st.warning(f"Admission saved, but fee schedule wasn't generated: {fee_error}")
        else:
            st.success(f"Admission record created. {months_created} month(s) of fees auto-generated for this student.")

        st.rerun()

@st.dialog("✏️ Edit Admission Record")
def edit_admission_dialog(selected_record):
    student_id = int(selected_record["Student_ID"])
    full_record = get_admission_dict(student_id)

    data = admission_form(full_record)

    if st.button("Update", use_container_width=True):

        values = (
            data["Previous_School"],
            data["Admission_Status"],
            data["Entrance_Test"],
            data["Admission_Fee"],
            data["Discount_Type"],
            data["Entrance_Test_Score"],
            data["Discount_Percentage"],
            student_id,
        )
        update_admission_record(values)
        st.success("Admission record updated successfully.")
        st.rerun()


@st.dialog("🗑 Delete Admission Record")
def delete_admission_dialog(selected_record):
    st.warning(
        f"Delete admission record for Student ID **{selected_record['Student_ID']}**? "
        f"This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_admission_record(selected_record["Student_ID"])
            st.success("Admission record deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
