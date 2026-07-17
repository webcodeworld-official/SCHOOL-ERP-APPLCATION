import streamlit as st


def show_visitor_table(visitors):

    if visitors.empty:
        st.warning("No visitor records found.")
        return []

    selected = st.dataframe(
        visitors[
            [
                "Visitor_ID",
                "Pass_No",
                "Visitor_Name",
                "Visitor_Type",
                "Purpose",
                "Visit_Date",
                "Check_In",
                "Check_Out"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return visitors.iloc[row_index]

    return []