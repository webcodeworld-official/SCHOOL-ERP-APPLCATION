import streamlit as st


def show_staff_cards(df):

    total_staff = len(df)
    active_staff = (df["Status"] == "Active").sum()
    teachers = df["Designation"].isin(["Teacher", "Senior Teacher"]).sum()
    total_departments = df["Department"].nunique()

    st.markdown('<div class="section-label">Staff Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total_staff, "👩‍🏫 Total Staff"),
        (active_staff, "✅ Active"),
        (teachers, "📖 Teachers"),
        (total_departments, "🏢 Departments"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)