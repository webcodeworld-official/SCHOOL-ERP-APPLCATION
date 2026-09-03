import streamlit as st


def show_visitor_table(visitors):

    if visitors.empty:
        st.warning("No visitor records found.")
        return []

    # Show everything except the raw Staff_ID key — Meeting_With / Meeting_With_Designation
    # (already joined in get_all_visitors) tell the same story more usefully.
    display_cols = [c for c in visitors.columns if c != "Staff_ID"]

    selected = st.dataframe(
        visitors[display_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return visitors.iloc[row_index]

    return []
