import streamlit as st
from datetime import date


def admission_form(record=None, unassigned_df=None):
    """
    Reusable Admission Record Form.

    If record=None -> Process a new admission (Add)
    If record has data -> Edit admission process details

    Returns dictionary containing all entered values.
    """

    if record is None:
        record = {}

    key_suffix = str(record.get("Student_ID", "new"))
    is_edit = "Student_ID" in record and record.get("Student_ID") is not None

    col1, col2 = st.columns(2)

    with col1:
        if is_edit:
            student_id = record["Student_ID"]
            st.text_input("Student ID", value=str(student_id), disabled=True, key=f"sid_{key_suffix}")
            st.text_input("Admission Date", value=str(record.get("Admission_Date", "")), disabled=True, key=f"adm_date_{key_suffix}")
        else:
            if unassigned_df is None or unassigned_df.empty:
                st.warning("No active students without an admission record.")
                student_id = None
            else:
                options = unassigned_df.apply(
                    lambda r: f"{r['Student_ID']} - {r['First_Name']} {r['Last_Name']} (Class {r['Class']}{r['Section']})",
                    axis=1
                ).tolist()
                choice = st.selectbox("Student", options, key=f"student_pick_{key_suffix}")
                student_id = int(choice.split(" - ")[0])
                match = unassigned_df[unassigned_df["Student_ID"] == student_id].iloc[0]
                st.caption(f"Enrolled on: {match['Admission_Date']}")

        previous_school = st.text_input(
            "Previous School",
            value=record.get("Previous_School", ""),
            key=f"prev_school_{key_suffix}"
        )

    with col2:
        status_options = ["Approved", "Pending"]
        admission_status = st.selectbox(
            "Admission Status",
            status_options,
            index=status_options.index(record.get("Admission_Status", "Pending")),
            key=f"status_{key_suffix}"
        )

        test_options = ["Pass", "N/A"]
        entrance_test = st.selectbox(
            "Entrance Test",
            test_options,
            index=test_options.index(record.get("Entrance_Test", "N/A")),
            key=f"test_{key_suffix}"
        )

        admission_fee = st.number_input(
            "Admission Fee",
            min_value=0,
            value=int(record.get("Admission_Fee", 1500)),
            key=f"fee_{key_suffix}"
        )

    st.divider()
    st.caption("Scholarship / Discount Eligibility")

    from database.admission_queries import DISCOUNT_TYPES, calculate_discount_percentage

    discount_type = st.selectbox(
        "Discount Type", DISCOUNT_TYPES,
        index=DISCOUNT_TYPES.index(record.get("Discount_Type") or "None"),
        key=f"discount_type_{key_suffix}"
    )

    entrance_test_score = None
    if discount_type == "Merit-Based":
        entrance_test_score = st.number_input(
            "Entrance Test Score (%)", min_value=0, max_value=100,
            value=int(record.get("Entrance_Test_Score") or 0),
            key=f"entrance_score_{key_suffix}"
        )

    calculated_percentage = calculate_discount_percentage(discount_type, entrance_test_score)
    st.info(f"📊 Calculated Discount: **{calculated_percentage}%**")

    return {
        "Student_ID": student_id,
        "Previous_School": previous_school,
        "Admission_Status": admission_status,
        "Entrance_Test": entrance_test,
        "Admission_Fee": admission_fee,
        "Discount_Type": discount_type,
        "Entrance_Test_Score": entrance_test_score,
        "Discount_Percentage": calculated_percentage,
    }
