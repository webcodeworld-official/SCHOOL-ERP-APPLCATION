import streamlit as st


def show_admission_table(records):

    if records.empty:
        st.warning("No admission records found.")
        return []

    selected = st.dataframe(
        records[
            [
                "Admission_ID",
                "Student_ID",
                "Admission_Date",
                "Previous_School",
                "Admission_Status",
                "Entrance_Test",
                "Admission_Fee"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return records.iloc[row_index]

    return []
