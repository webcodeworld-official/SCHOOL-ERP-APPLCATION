import streamlit as st
import pandas as pd
from datetime import date


def show_library_table(records):

    if records.empty:
        st.warning("No library records found.")
        return []

    display_df = records.copy()

    today = date.today()

    def compute_status(row):
        if pd.notna(row["Return_Date"]):
            return "Returned"
        due = date.fromisoformat(str(row["Due_Date"]))
        return "Overdue" if due < today else "Issued"

    display_df["Status"] = display_df.apply(compute_status, axis=1)

    selected = st.dataframe(
        display_df[
            [
                "Transaction_ID",
                "Student_ID",
                "Book_Name",
                "Issue_Date",
                "Due_Date",
                "Return_Date",
                "Fine",
                "Status"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return display_df.iloc[row_index]

    return []
