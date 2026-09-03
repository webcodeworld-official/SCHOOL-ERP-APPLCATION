import streamlit as st
from datetime import date, datetime


def _parse_date(value, default):
    if not value:
        return default
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return default


def student_form(student=None):
    """
    Reusable Student Form.

    If student=None -> Add Student
    If student has data -> Edit Student

    Returns dictionary containing all entered values, PLUS raw uploaded file
    objects under "Photo_File" and "Aadhar_Doc_File" keys (the dialog is
    responsible for saving these to disk and storing the resulting path).
    """

    if student is None:
        student = {}

    key_suffix = str(student.get("Student_ID", "new"))

    col1, col2 = st.columns(2)

    with col1:
        student_id = st.text_input(
            "Student ID", value=str(student.get("Student_ID", "")),
            disabled=True, key=f"student_id_{key_suffix}"
        )
        first_name = st.text_input(
            "First Name", value=student.get("First_Name", ""),
            key=f"first_name_{key_suffix}"
        )

    with col2:
        admission_no = st.text_input(
            "Admission Number", value=str(student.get("Admission_No", "")),
            disabled=True, key=f"admission_no_{key_suffix}"
        )
        last_name = st.text_input(
            "Last Name", value=student.get("Last_Name", ""),
            key=f"last_name_{key_suffix}"
        )

    st.divider()
    st.caption("Academic Details")

    col3, col4, col5 = st.columns(3)

    with col3:
        roll_no = st.text_input(
            "Roll Number", value=str(student.get("Roll_No", "")),
            key=f"roll_no_{key_suffix}"
        )
        student_class = st.selectbox(
            "Class Enrolling Into", [str(i) for i in range(1, 13)],
            index=max(int(student.get("Class", "1")) - 1, 0),
            key=f"class_{key_suffix}"
        )
        stream = None
        if student_class in ("11", "12"):
            stream_options = ["Science", "Commerce", "Arts"]
            current_stream = student.get("Stream") or "Science"
            stream = st.selectbox(
                "Stream", stream_options,
                index=stream_options.index(current_stream),
                key=f"stream_{key_suffix}"
            )

    with col4:
        section = st.selectbox(
            "Section", ["A", "B", "C"],
            index=["A", "B", "C"].index(student.get("Section", "A")),
            key=f"section_{key_suffix}"
        )
        house_options = ["Red", "Blue", "Green", "Yellow"]
        house = st.selectbox(
            "House", house_options,
            index=house_options.index(student.get("House") or "Yellow"),
            key=f"house_{key_suffix}"
        )

    with col5:
        fee_category_options = ["General", "Scholarship", "Sibling"]
        fee_category = st.selectbox(
            "Fee Category", fee_category_options,
            index=fee_category_options.index(student.get("Fee_Category") or "General"),
            key=f"fee_category_{key_suffix}"
        )
        status = st.selectbox(
            "Status", ["Active", "Inactive"],
            index=0 if student.get("Status", "Active") == "Active" else 1,
            key=f"status_{key_suffix}"
        )

    st.divider()
    st.caption("Personal Details")

    col6, col7 = st.columns(2)

    with col6:
        gender = st.selectbox(
            "Gender", ["Male", "Female"],
            index=0 if student.get("Gender", "Male") == "Male" else 1,
            key=f"gender_{key_suffix}"
        )
        date_of_birth = st.date_input(
            "Date of Birth",
            value=_parse_date(student.get("Date_of_Birth"), date(2015, 1, 1)),
            min_value=date(1990, 1, 1), max_value=date.today(),
            key=f"dob_{key_suffix}"
        )

    with col7:
        blood_group_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
        blood_group = st.selectbox(
            "Blood Group", blood_group_options,
            index=blood_group_options.index(student.get("Blood_Group") or "Unknown"),
            key=f"blood_group_{key_suffix}"
        )

    st.divider()
    st.caption("Parent & Contact Details")

    col8, col9 = st.columns(2)

    with col8:
        father_name = st.text_input("Father's Name", value=student.get("Father_Name", ""), key=f"father_name_{key_suffix}")
        email = st.text_input("Email", value=student.get("Email", ""), key=f"email_{key_suffix}")

    with col9:
        mother_name = st.text_input("Mother's Name", value=student.get("Mother_Name", ""), key=f"mother_name_{key_suffix}")

    # --- State + City dropdowns (State drives City's options) ---
    from utils import STATE_CITY_MAP, ALL_STATES

    col_state, col_city = st.columns(2)

    with col_state:
        current_state = student.get("State") or "Uttar Pradesh"
        state_index = ALL_STATES.index(current_state) if current_state in ALL_STATES else ALL_STATES.index("Other")
        state = st.selectbox("State", ALL_STATES, index=state_index, key=f"state_{key_suffix}")

    with col_city:
        if state == "Other":
            city = st.text_input("City", value=student.get("City", ""), key=f"city_{key_suffix}")
        else:
            city_options = STATE_CITY_MAP.get(state, []) + ["Other"]
            current_city = student.get("City") or city_options[0]
            city_index = city_options.index(current_city) if current_city in city_options else city_options.index("Other")
            city = st.selectbox("City", city_options, index=city_index, key=f"city_select_{key_suffix}")
            if city == "Other":
                city = st.text_input("Enter City", value="", key=f"city_other_{key_suffix}")

    # --- Country + Parent Mobile ---
    from utils import COUNTRY_OPTIONS, split_stored_phone

    default_region, default_number = split_stored_phone(student.get("Parent_Mobile"))

    col_code, col_number = st.columns([1, 2])
    with col_code:
        country_names = list(COUNTRY_OPTIONS.keys())
        region_to_name = {v: k for k, v in COUNTRY_OPTIONS.items()}
        default_country_name = region_to_name.get(default_region, country_names[0])
        selected_country = st.selectbox(
            "Country", country_names,
            index=country_names.index(default_country_name),
            key=f"country_{key_suffix}"
        )
        selected_region = COUNTRY_OPTIONS[selected_country]

    with col_number:
        parent_mobile_raw = st.text_input(
            "Parent Mobile",
            value=default_number,
            key=f"parent_mobile_{key_suffix}"
        )

    st.divider()
    st.caption("Photo & Document Verification")

    col10, col11 = st.columns(2)

    with col10:
        if student.get("Photo_Path"):
            st.image(student["Photo_Path"], width=120, caption="Current photo")
        photo_file = st.file_uploader(
            "Upload Student Photo", type=["jpg", "jpeg", "png"],
            key=f"photo_{key_suffix}"
        )

    with col11:
        aadhar_no = st.text_input(
            "Aadhar Number (12 digits)", value=student.get("Aadhar_No", ""),
            max_chars=12, key=f"aadhar_no_{key_suffix}"
        )
        if student.get("Aadhar_Doc_Path"):
            st.caption(f"📄 Document already uploaded: {student['Aadhar_Doc_Path'].split('/')[-1]}")
        aadhar_doc_file = st.file_uploader(
            "Upload Aadhar Card (image or PDF)", type=["jpg", "jpeg", "png", "pdf"],
            key=f"aadhar_doc_{key_suffix}"
        )

    return {
        "Admission_No": admission_no,
        "Roll_No": roll_no,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Gender": gender,
        "Class": student_class,
        "Stream": stream,
        "Section": section,
        "Parent_Mobile_Raw": parent_mobile_raw,
        "Parent_Mobile_Region": selected_region,
        "Status": status,
        "Date_of_Birth": date_of_birth,
        "Blood_Group": None if blood_group == "Unknown" else blood_group,
        "Father_Name": father_name,
        "Mother_Name": mother_name,
        "Email": email,
        "City": city,
        "State": state,
        "House": house,
        "Fee_Category": fee_category,
        "Aadhar_No": aadhar_no,
        "Photo_File": photo_file,
        "Aadhar_Doc_File": aadhar_doc_file,
    }
