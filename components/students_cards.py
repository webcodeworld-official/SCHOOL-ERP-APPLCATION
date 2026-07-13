import streamlit as st


def show_student_cards(students):

    boys = (students["Gender"] == "Male").sum()
    girls = (students["Gender"] == "Female").sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "👨‍🎓 Total Students",
        len(students)
    )

    c2.metric(
        "👦 Boys",
        boys
    )

    c3.metric(
        "👧 Girls",
        girls
    )

    c4.metric(
        "🏫 Classes",
        students["Class"].nunique()
    )