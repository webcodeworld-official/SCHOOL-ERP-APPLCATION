import streamlit as st
from datetime import date
from database.fees_queries import (
    add_fee_record, update_fee_record, delete_fee_record,
    get_next_payment_id, get_active_students, get_fee_dict,
    fee_record_exists, record_payment
)
from components.fees_form import fees_form


@st.dialog("💰 Add Fee Record")
def add_fee_dialog():
    students_df = get_active_students(branch_id=st.session_state.get("active_branch_id"))
    data = fees_form(students_df=students_df)
    if st.button("Create", use_container_width=True):

        if data["Student_ID"] is None:
            st.error("No student selected.")
            return

        if fee_record_exists(data["Student_ID"], data["Month"]):
            st.error(f"A fee record for this student in {data['Month']} already exists.")
            return

        payment_id = get_next_payment_id()

        add_fee_record(
            payment_id,
            data["Student_ID"],
            data["Month"],
            data["Tuition_Fee"],
            data["Transport_Fee"],
            data["Library_Fee"],
            data["Exam_Fee"],
            data["Discount"],
        )

        st.success(f"Fee record created. Total due: ₹{data['Total_Fee']}")
        st.rerun()


@st.dialog("✏️ Edit Fee Record")
def edit_fee_dialog(selected_record):
    payment_id = int(selected_record["Payment_ID"])
    full_record = get_fee_dict(payment_id)

    data = fees_form(full_record)

    if st.button("Update", use_container_width=True):

        update_fee_record(
            payment_id,
            data["Tuition_Fee"],
            data["Transport_Fee"],
            data["Library_Fee"],
            data["Exam_Fee"],
            data["Discount"],
        )

        st.success("Fee record updated successfully.")
        st.rerun()


@st.dialog("💳 Record Payment")
def record_payment_dialog(selected_record):
    payment_id = int(selected_record["Payment_ID"])

    if selected_record.get("Payment_Status") == "Paid":
        st.warning("This fee record is already fully paid.")
        if st.button("Close", use_container_width=True):
            st.rerun()
        return

    balance = selected_record["Balance"]

    st.write(f"**Student ID:** {selected_record['Student_ID']}")
    st.write(f"**Month:** {selected_record['Month']}")
    st.write(f"**Total Fee:** ₹{selected_record['Total_Fee']}")
    st.write(f"**Already Paid:** ₹{selected_record['Amount_Paid']}")
    st.write(f"**Balance Due:** ₹{balance}")

    amount = st.number_input(
        "Payment Amount",
        min_value=1,
        max_value=int(balance),
        value=int(balance)
    )

    payment_mode = st.selectbox("Payment Mode", ["Cash", "Card", "UPI", "Bank Transfer"])

    if st.button("Confirm Payment", use_container_width=True):
        new_paid, new_balance, status = record_payment(
            payment_id, amount, payment_mode, date.today().isoformat()
        )
        st.success(f"Payment recorded. New status: {status}. Remaining balance: ₹{new_balance}")
        st.rerun()


@st.dialog("🗑 Delete Fee Record")
def delete_fee_dialog(selected_record):
    st.warning(
        f"Delete fee record for Student ID **{selected_record['Student_ID']}** "
        f"({selected_record['Month']})? This cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            delete_fee_record(selected_record["Payment_ID"])
            st.success("Fee record deleted.")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
