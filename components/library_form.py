import streamlit as st
from datetime import date, datetime, timedelta


def _parse_date(value, default):
    if not value:
        return default
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return default


def library_form(record=None):
    """
    Reusable Library Issue Form.

    If record=None -> Issue a new book (Return_Date/Fine not asked, always NULL at issue)
    If record has data -> Edit issue details (Return_Date/Fine untouched here;
                           use the dedicated Return Book dialog for that)

    Returns dictionary containing all entered values.
    """

    if record is None:
        record = {}

    key_suffix = str(record.get("Transaction_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        transaction_id = st.text_input(
            "Transaction ID",
            value=str(record.get("Transaction_ID", "")),
            disabled=True,
            key=f"transaction_id_{key_suffix}"
        )

        student_id = st.text_input(
            "Student ID",
            value=str(record.get("Student_ID", "")),
            key=f"student_id_{key_suffix}"
        )

        book_id = st.text_input(
            "Book ID",
            value=str(record.get("Book_ID", "")),
            key=f"book_id_{key_suffix}"
        )

        book_name = st.text_input(
            "Book Name",
            value=record.get("Book_Name", ""),
            key=f"book_name_{key_suffix}"
        )

    with col2:
        issue_date = st.date_input(
            "Issue Date",
            value=_parse_date(record.get("Issue_Date"), date.today()),
            max_value=date.today(),
            key=f"issue_date_{key_suffix}"
        )

        due_date = st.date_input(
            "Due Date",
            value=_parse_date(record.get("Due_Date"), date.today() + timedelta(days=14)),
            key=f"due_date_{key_suffix}"
        )

        if record.get("Return_Date"):
            st.caption(f"✅ Returned on {record['Return_Date']} — Fine: ₹{record.get('Fine', 0)}")
        elif record.get("Transaction_ID"):
            st.caption("📕 Currently issued — not yet returned")

    return {
        "Student_ID": student_id,
        "Book_ID": book_id,
        "Book_Name": book_name,
        "Issue_Date": issue_date,
        "Due_Date": due_date,
    }
