import streamlit as st


def show_student_table(students):

    if students.empty:
        st.warning("No student records found.")
        return []

    selected = st.dataframe(
        students[
            [
                "Student_ID",
                "Admission_No",
                "Roll_No",
                "Full_Name",
                "Class",
                "Section"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:

        row_index = selected.selection.rows[0]

        return students.iloc[row_index]

    return []