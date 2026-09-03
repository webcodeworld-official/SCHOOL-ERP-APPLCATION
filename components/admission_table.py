import streamlit as st


def show_admission_table(records):

    if records.empty:
        st.warning("No admission records found.")
        return []

    selected = st.dataframe(
        records,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return records.iloc[row_index]

    return []
