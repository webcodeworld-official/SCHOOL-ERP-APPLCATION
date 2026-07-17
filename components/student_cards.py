import streamlit as st


def show_student_cards(df):

    total_students = len(df)
    boys = (df["Gender"] == "Male").sum()
    girls = (df["Gender"] == "Female").sum()
    total_classes = df["Class"].nunique()

    st.markdown('<div class="section-label">Student Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total_students, "👨‍🎓 Total Students"),
        (boys, "👦 Boys"),
        (girls, "👧 Girls"),
        (total_classes, "🏫 Classes"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)