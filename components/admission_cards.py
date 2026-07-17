import streamlit as st


def show_admission_cards(df):

    total = len(df)
    approved = (df["Admission_Status"] == "Approved").sum()
    pending = (df["Admission_Status"] == "Pending").sum()
    passed_test = (df["Entrance_Test"] == "Pass").sum()

    st.markdown('<div class="section-label">Admission Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total, "📥 Total Admissions"),
        (approved, "✅ Approved"),
        (pending, "⏳ Pending"),
        (passed_test, "📝 Entrance Test Passed"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
