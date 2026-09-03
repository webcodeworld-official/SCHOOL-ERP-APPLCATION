import streamlit as st


def show_staff_table(staff):

    if staff.empty:
        st.warning("No staff records found.")
        return []

    selected = st.dataframe(
        staff,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:

        row_index = selected.selection.rows[0]

        return staff.iloc[row_index]

    return []