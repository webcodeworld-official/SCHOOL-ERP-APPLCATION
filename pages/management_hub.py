import streamlit as st
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">ERP Management</div>
    <div class="erp-title">Run the day-to-day of your school.</div>
    <div class="erp-subtitle">
        Add, edit, and manage records across every department — students, staff,
        fees, library, transport, and examinations, all from one place.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin: 0.5rem 0 2rem 0;">
    <svg width="200" height="140" viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg">
        <rect x="40" y="30" width="120" height="90" rx="8" fill="#27272A" stroke="#3F3F46" stroke-width="2"/>
        <rect x="55" y="45" width="90" height="8" rx="3" fill="#14B8A6"/>
        <rect x="55" y="62" width="60" height="6" rx="3" fill="#A1A1AA"/>
        <rect x="55" y="76" width="70" height="6" rx="3" fill="#A1A1AA"/>
        <rect x="55" y="90" width="45" height="6" rx="3" fill="#A1A1AA"/>
        <circle cx="145" cy="100" r="18" fill="#14B8A6" opacity="0.15"/>
        <path d="M145 90 L145 95 M145 105 L145 110 M135 100 L140 100 M150 100 L155 100
                 M138 93 L141 96 M149 104 L152 107 M138 107 L141 104 M149 96 L152 93"
              stroke="#14B8A6" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="145" cy="100" r="6" fill="#14B8A6"/>
    </svg>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Choose a Module</div>', unsafe_allow_html=True)

modules = [
    ("👨‍🎓", "Student Management", "Admissions, records, and class assignments", "pages/09_Student_Management.py"),
    ("📥", "Admission Management", "Process admissions, entrance tests, and approvals", "pages/16_Admission_Management.py"),
    ("👩‍🏫", "Staff Management", "Employee records and departments", "pages/10_Staff_Management.py"),
    ("🚶", "Visitor Management", "Front-desk check-in and visit logs", "pages/11_Visitor_Management.py"),
    ("📚", "Library Management", "Book issues, returns, and fines", "pages/12_Library_Management.py"),
    ("🚌", "Transport Management", "Bus routes and student assignments", "pages/13_Transport_Management.py"),
    ("💰", "Fee Management", "Invoicing, payments, and balances", "pages/14_Fee_Management.py"),
    ("📝", "Examination Management", "Bulk marks entry and results", "pages/15_Examination_Management.py"),
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
            if st.button("Open →", use_container_width=True, key=f"management_{title}"):
                st.switch_page(path)
    st.write("")