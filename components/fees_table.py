import streamlit as st


def show_fees_table(records):

    if records.empty:
        st.warning("No fee records found.")
        return []

    selected = st.dataframe(
        records[
            [
                "Payment_ID",
                "Student_ID",
                "Month",
                "Total_Fee",
                "Amount_Paid",
                "Balance",
                "Payment_Mode",
                "Payment_Status"
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
