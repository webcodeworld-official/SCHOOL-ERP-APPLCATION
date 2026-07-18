import streamlit as st
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">Analytics</div>
    <div class="erp-title">See how your school is really doing.</div>
    <div class="erp-subtitle">
        Explore trends, performance, and KPIs across every part of the school —
        from enrollment and attendance to fee collection and exam results.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin: 0.5rem 0 2rem 0;">
    <svg width="220" height="140" viewBox="0 0 220 140" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="90" width="30" height="40" rx="3" fill="#14B8A6" opacity="0.85"/>
        <rect x="50" y="60" width="30" height="70" rx="3" fill="#14B8A6"/>
        <rect x="90" y="30" width="30" height="100" rx="3" fill="#2DD4BF"/>
        <rect x="130" y="70" width="30" height="60" rx="3" fill="#14B8A6" opacity="0.85"/>
        <rect x="170" y="45" width="30" height="85" rx="3" fill="#2DD4BF"/>
        <path d="M15 85 L65 55 L105 25 L145 65 L185 40" stroke="#FBBF24" stroke-width="3" fill="none" stroke-linecap="round"/>
        <circle cx="185" cy="40" r="5" fill="#FBBF24"/>
    </svg>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Choose a Module</div>', unsafe_allow_html=True)

modules = [
    ("🎓", "Students Analytics", "Enrollment, demographics, and class-wise trends", "pages/01_Students_Analytics.py"),
    ("👩‍🏫", "Staff Analytics", "Department strength, experience, and payroll trends", "pages/02_Staff_Analytics.py"),
    ("🚶", "Visitors Analytics", "Visitor patterns by type and purpose", "pages/03_Visitors_Analytics.py"),
    ("🚌", "Transportation Analytics", "Route usage and transport revenue", "pages/04_Transportation_Analytics.py"),
    ("📥", "Admission Analytics", "Admission trends and approval rates", "pages/05_Admission_Analytics.py"),
    ("📝", "Examination Analytics", "Pass rates, averages, and top performers", "pages/06_Examination_Analytics.py"),
    ("💰", "Fees Analytics", "Collection trends and outstanding balances", "pages/07_Fees_Analytics.py"),
    ("📚", "Library Analytics", "Circulation, overdue books, and fines", "pages/08_Library_Analytics.py"),
]

for row_start in range(0, len(modules), 4):
    row = modules[row_start:row_start + 4]
    cols = st.columns(4)
    for col, (icon, title, desc, path) in zip(cols, row):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open →", use_container_width=True, key=f"analytics_{title}"):
                st.switch_page(path)
    st.write("")