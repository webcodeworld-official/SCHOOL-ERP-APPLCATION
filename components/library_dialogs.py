import streamlit as st
from datetime import date, timedelta
from database.library_queries import (
    issue_book, update_library_record, delete_library_record,
    get_next_transaction_id, get_library_record_dict, return_book
)
from components.library_form import library_form

@st.dialog("📕 Issue Book")
def issue_book_dialog():

    next_id = get_next_transaction_id()
    preview = {"Transaction_ID": next_id}

    data = library_form(preview)

    active_branch_id = st.session_state.get("active_branch_id")
    if active_branch_id is None:
        from database.branch_queries import get_all_branches
        branches = get_all_branches()
        if branches.empty:
            st.error("No branches exist yet. Add a branch first (Settings).")
            branch_id_for_issue = None
        else:
            branch_choice = st.selectbox(
                "Which Branch's library?", branches["Branch_Name"].tolist(), key="issue_book_branch_pick"
            )
            branch_id_for_issue = int(
                branches[branches["Branch_Name"] == branch_choice]["Branch_ID"].iloc[0]
            )
    else:
        branch_id_for_issue = active_branch_id

    if st.button("Issue", use_container_width=True):

        if not data["Student_ID"]:
            st.error("Student ID is required.")
            return

        if not data["Book_Name"]:
            st.error("Book Name is required.")
            return

        if data["Due_Date"] < data["Issue_Date"]:
            st.error("Due Date cannot be before Issue Date.")
            return

        if branch_id_for_issue is None:
            st.error("A branch must be selected.")
            return

        values = (
            next_id,
            data["Student_ID"],
            data["Book_ID"],
            data["Book_Name"],
            str(data["Issue_Date"]),
            str(data["Due_Date"]),
            branch_id_for_issue,
        )

        issue_book(values)
        st.success(f"Book issued successfully. Transaction ID: {next_id}")
        st.rerun()

@st.dialog("✏️ Edit Issue Details")
def edit_library_dialog(selected_record):
    transaction_id = int(selected_record["Transaction_ID"])
    full_record = get_library_record_dict(transaction_id)

    data = library_form(full_record)

    if st.button("Update", use_container_width=True):

        if data["Due_Date"] < data["Issue_Date"]:
            st.error("Due Date cannot be before Issue Date.")
            return

        values = (
            data["Student_ID"],
            data["Book_ID"],
            data["Book_Name"],
            str(data["Issue_Date"]),
            str(data["Due_Date"]),
            transaction_id,
        )

        update_library_record(values)
        st.success("Issue details updated successfully.")
        st.rerun()


@st.dialog("📗 Return Book")
def return_book_dialog(selected_record):
    transaction_id = int(selected_record["Transaction_ID"])

    if selected_record.get("Return_Date"):
        st.warning("This book has already been returned.")
        if st.button("Close", use_container_width=True):
            st.rerun()
        return

    st.write(f"**Book:** {selected_record['Book_Name']}")
    st.write(f"**Student ID:** {selected_record['Student_ID']}")
    st.write(f"**Due Date:** {selected_record['Due_Date']}")

    return_date = st.date_input(
        "Return Date",
        value=date.today(),
        max_value=date.today()
    )

    due_date = date.fromisoformat(str(selected_record["Due_Date"]))
    days_late = max((return_date - due_date).days, 0)
    projected_fine = days_late * 5

    if days_late > 0:
        st.warning(f"⚠️ {days_late} day(s) late — Fine: ₹{projected_fine}")
    else:
        st.success("On time — no fine.")

    if st.button("Confirm Return", use_container_width=True):
        fine = return_book(transaction_id, return_date)
        st.success(f"Book returned. Fine charged: ₹{fine}")
        st.rerun()


@st.dialog("🗑 Delete Record")
def delete_library_dialog(selected_record):
    st.warning(
        f"Are you sure you want to delete this transaction "
        f"(Book: **{selected_record['Book_Name']}**, Student ID: {selected_record['Student_ID']})? "
        f"This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_library_record(selected_record["Transaction_ID"])
            st.success("Record deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
