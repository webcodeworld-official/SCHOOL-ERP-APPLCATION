import streamlit as st
import database.student_queries as sq

st.write(sq.__file__)


@st.dialog("➕ Add New Student")
def add_student_dialog():

    next_student_id = sq.get_next_student_id()

    with st.form("add_student_form"):

        col1, col2 = st.columns(2)

        with col1:
            student_id = st.text_input(
                "Student ID",
                value=str(next_student_id),
                disabled=True
            )

            admission_no = st.text_input(
                "Admission Number"
            )

            first_name = st.text_input(
                "First Name"
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female"]
            )

        with col2:
            roll_no = st.number_input(
                "Roll Number",
                min_value=1,
                step=1
            )

            last_name = st.text_input(
                "Last Name"
            )

            student_class = st.selectbox(
                "Class",
                ["1","2","3","4","5","6","7","8","9","10","11","12"]
            )

            section = st.selectbox(
                "Section",
                ["A","B","C","D"]
            )

        submitted = st.form_submit_button("💾 Save Student")

        if submitted:

            sq.add_student(
                (
                    int(student_id),
                    admission_no,
                    roll_no,
                    first_name,
                    last_name,
                    gender,
                    "",                 # Date_of_Birth
                    student_class,
                    section,
                    "",                 # House
                    "",                 # Admission_Date
                    "",                 # Academic_Year
                    "",                 # Father_Name
                    "",                 # Mother_Name
                    "",                 # Parent_Mobile
                    "",                 # Email
                    "",                 # City
                    "",                 # State
                    "",                 # Transport_ID
                    "",                 # Fee_Category
                    "",                 # Blood_Group
                    "Active"
                )
            )

            st.success("✅ Student Added Successfully!")

            st.rerun()
