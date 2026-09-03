import streamlit as st
from database.fees_queries import ACADEMIC_MONTHS, get_student_transport_fee


def fees_form(record=None, students_df=None):
    """
    Reusable Fee Record Form.

    If record=None -> Create a new fee due record (Add)
    If record has data -> Edit fee components of an existing record

    Returns dictionary containing all entered values.
    """

    if record is None:
        record = {}

    key_suffix = str(record.get("Payment_ID", "new"))
    is_edit = "Payment_ID" in record and record.get("Payment_ID") is not None

    col1, col2 = st.columns(2)

    with col1:
        if is_edit:
            student_id = record["Student_ID"]
            st.text_input("Student ID", value=str(student_id), disabled=True, key=f"sid_{key_suffix}")
            st.text_input("Month", value=record.get("Month", ""), disabled=True, key=f"month_{key_suffix}")
            month = record.get("Month")
            auto_transport_fee = record.get("Transport_Fee", 0)
        else:
            if students_df is None or students_df.empty:
                st.warning("No active students available.")
                student_id = None
                auto_transport_fee = 0
            else:
                options = students_df.apply(
                    lambda r: f"{r['Student_ID']} - {r['First_Name']} {r['Last_Name']} (Class {r['Class']}{r['Section']})",
                    axis=1
                ).tolist()
                choice = st.selectbox("Student", options, key=f"student_pick_{key_suffix}")
                student_id = int(choice.split(" - ")[0])
                auto_transport_fee = get_student_transport_fee(student_id)

            month = st.selectbox("Month", ACADEMIC_MONTHS, key=f"month_pick_{key_suffix}")

        tuition_fee = st.number_input(
            "Tuition Fee",
            min_value=0,
            value=int(record.get("Tuition_Fee", 3000)),
            key=f"tuition_{key_suffix}"
        )

        transport_fee = st.number_input(
            "Transport Fee",
            min_value=0,
            value=int(record.get("Transport_Fee", auto_transport_fee)),
            key=f"transport_{key_suffix}"
        )

    with col2:
        library_fee = st.number_input(
            "Library Fee",
            min_value=0,
            value=int(record.get("Library_Fee", 100)),
            key=f"library_{key_suffix}"
        )

        exam_fee = st.number_input(
            "Exam Fee",
            min_value=0,
            value=int(record.get("Exam_Fee", 0)),
            key=f"exam_{key_suffix}"
        )

        from database.admission_queries import get_admission_discount_percentage

        default_discount = record.get("Discount", 0)
        if not is_edit and student_id:
            discount_pct = get_admission_discount_percentage(student_id)
            if discount_pct > 0:
                default_discount = int(tuition_fee * discount_pct / 100)
                st.caption(f"💡 Auto-suggested from Admission record: {discount_pct}% discount")

        discount_key_suffix = f"{key_suffix}_{student_id}"

        discount = st.number_input(
            "Discount",
            min_value=0,
            value=int(default_discount),
            key=f"discount_{discount_key_suffix}"
        )

        total_fee = tuition_fee + transport_fee + library_fee + exam_fee - discount
        st.metric("Total Fee", f"₹{total_fee}")

        if is_edit:
            st.caption(
                f"Already paid: ₹{record.get('Amount_Paid', 0)} | "
                f"Status: {record.get('Payment_Status', 'Pending')}"
            )

    return {
        "Student_ID": student_id,
        "Month": month,
        "Tuition_Fee": tuition_fee,
        "Transport_Fee": transport_fee,
        "Library_Fee": library_fee,
        "Exam_Fee": exam_fee,
        "Discount": discount,
        "Total_Fee": total_fee,
    }
