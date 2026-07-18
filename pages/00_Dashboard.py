import streamlit as st
from datetime import datetime, date
import pandas as pd

from database.connection import get_connection
from database.library_queries import get_all_library_records
from database.fees_queries import get_all_fees
from database.examination_queries import get_all_results
from utils import load_custom_css

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Session expired. Please log in again.")
    st.stop()

with st.sidebar:
    st.markdown(f"**{st.session_state.get('full_name', 'User')}**")
    st.caption(f"Role: {st.session_state.get('role', 'Unknown')}")
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
# --------------------------------------------------
# LIVE DATA
# --------------------------------------------------

conn = get_connection()
students = pd.read_sql("SELECT * FROM student", conn)
staff = pd.read_sql("SELECT * FROM staff", conn)
visitors = pd.read_sql("SELECT * FROM visitors", conn)
transport = pd.read_sql("SELECT * FROM transportation", conn)
attendance_today = pd.read_sql(
    "SELECT * FROM attendence WHERE Date = ?", conn, params=(date.today().isoformat(),)
)
conn.close()

library = get_all_library_records()
fees = get_all_fees()
exam = get_all_results()

active_students = students[students["Status"] == "Active"]
active_staff = staff[staff["Status"] == "Active"]

overdue_books = library[
    library["Return_Date"].isna()
    & (pd.to_datetime(library["Due_Date"]) < pd.Timestamp(date.today()))
].shape[0]

pending_fees_count = fees[fees["Payment_Status"] == "Pending"].shape[0]
pending_fees_amount = fees[fees["Payment_Status"] == "Pending"]["Balance"].sum()

absent_today = attendance_today[attendance_today["Status"] == "Absent"].shape[0]

total_students = len(active_students)
total_staff = len(active_staff)
total_visitors_month = visitors[
    pd.to_datetime(visitors["Visit_Date"]) >= (pd.Timestamp(date.today()) - pd.Timedelta(days=30))
].shape[0]
total_routes = transport["Transport_ID"].nunique()

attendance_pct = (
    attendance_today["Status"].isin(["Present", "Late"]).mean() * 100
    if not attendance_today.empty else 0
)
avg_exam_pct = exam["Percentage"].mean() if not exam.empty else 0

total_collected = fees["Amount_Paid"].sum()
collection_rate = (fees["Amount_Paid"].sum() / fees["Total_Fee"].sum() * 100) if fees["Total_Fee"].sum() > 0 else 0

# --------------------------------------------------
# HERO
# --------------------------------------------------

now = datetime.now()
greeting = "morning" if now.hour < 12 else "afternoon" if now.hour < 18 else "evening"

hero_col1, hero_col2 = st.columns([2.2, 1])

with hero_col1:
    st.markdown(f"""
    <div class="erp-hero" style="min-height:200px; display:flex; flex-direction:column; justify-content:center;">
        <div class="erp-eyebrow">School ERP System</div>
        <div class="erp-title">Good {greeting}. Welcome back.</div>
        <div class="erp-subtitle">
            {now.strftime('%A, %d %B %Y')} · {now.strftime('%I:%M %p')} · Academic Year 2026-2027
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_col2:
    st.markdown("""
    <div class="erp-hero" style="min-height:200px; display:flex; align-items:center; justify-content:center; padding:1.2rem;">
        <svg width="140" height="140" viewBox="0 0 140 140" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="70" cy="70" r="65" fill="#14B8A6" opacity="0.08"/>
            <rect x="35" y="70" width="70" height="38" rx="4" fill="#14B8A6"/>
            <rect x="35" y="70" width="70" height="8" fill="#0D9488"/>
            <rect x="46" y="82" width="14" height="26" fill="#27272A"/>
            <rect x="80" y="82" width="14" height="14" fill="#27272A"/>
            <path d="M70 34 L108 52 L70 70 L32 52 Z" fill="#FAFAFA"/>
            <path d="M70 70 L70 84" stroke="#FAFAFA" stroke-width="2"/>
            <circle cx="70" cy="86" r="3" fill="#FAFAFA"/>
            <path d="M45 48 V60 Q45 66 51 66 H89 Q95 66 95 60 V48" stroke="#14B8A6" stroke-width="2" fill="none"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
# --------------------------------------------------
# QUICK NAVIGATION → HUBS
# --------------------------------------------------

st.markdown('<div class="section-label">Get Started</div>', unsafe_allow_html=True)

nav1, nav2 = st.columns(2)

with nav1:
    st.markdown("""
    <div class="nav-card">
        <h3>📊 Analytics</h3>
        <p>Explore trends, KPIs, and reports across every module — students, staff,
        fees, examinations, attendance, and more.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Analytics →", use_container_width=True, key="nav_analytics"):
        st.switch_page("pages/analytics_hub.py")

with nav2:
    st.markdown("""
    <div class="nav-card">
        <h3>⚙️ ERP Management</h3>
        <p>Add, edit, and manage records — student admissions, staff, fees, library,
        transport, and exams.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Management →", use_container_width=True, key="nav_management"):
        st.switch_page("pages/management_hub.py")

# --------------------------------------------------
# WHAT THIS APP COVERS
# --------------------------------------------------

st.markdown('<div class="section-label">Everything In One System</div>', unsafe_allow_html=True)

feature_row1 = st.columns(4)
features_1 = [
    ("🎓", "Students", "Admissions, records, and class assignments"),
    ("👩‍🏫", "Staff", "Employee records, departments, and payroll basics"),
    ("💰", "Fees", "Invoicing, payments, and collection tracking"),
    ("📚", "Library", "Book issues, returns, and overdue fines"),
]
for col, (icon, title, desc) in zip(feature_row1, features_1):
    col.markdown(f"""
    <div class="feature-card">
        <div class="icon">{icon}</div>
        <h4>{title}</h4>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

feature_row2 = st.columns(4)
features_2 = [
    ("🚌", "Transport", "Bus routes, driver info, and student assignments"),
    ("📝", "Examinations", "Bulk marks entry, grading, and results"),
    ("🚶", "Visitors", "Front-desk logging for guests and parents"),
    ("📊", "Analytics", "Live dashboards across every module"),
]
for col, (icon, title, desc) in zip(feature_row2, features_2):
    col.markdown(f"""
    <div class="feature-card">
        <div class="icon">{icon}</div>
        <h4>{title}</h4>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# NEEDS ATTENTION
# --------------------------------------------------

st.markdown('<div class="section-label">Needs Attention</div>', unsafe_allow_html=True)

attn_items = [
    (overdue_books, "Books Overdue", overdue_books > 0),
    (pending_fees_count, "Fee Payments Pending", pending_fees_count > 0),
    (absent_today, "Students Absent Today", absent_today > 5),
]

cols = st.columns(len(attn_items))
for col, (num, label, is_urgent) in zip(cols, attn_items):
    css_class = "attn-card" if is_urgent else "attn-card calm"
    with col:
        st.markdown(f"""
        <div class="{css_class}">
            <div class="attn-num">{num}</div>
            <div class="attn-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

if pending_fees_amount > 0:
    st.caption(f"₹{pending_fees_amount:,.0f} in fees currently outstanding across {pending_fees_count} record(s).")

# --------------------------------------------------
# KPI GROUPS
# --------------------------------------------------

st.markdown('<div class="section-label">Academic</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
for col, (val, label) in zip(
    [c1, c2, c3, c4],
    [
        (total_students, "Active Students"),
        (total_staff, "Active Staff"),
        (f"{attendance_pct:.1f}%", "Attendance Today"),
        (f"{avg_exam_pct:.1f}%", "Avg Exam Score"),
    ]
):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-label">Operations</div>', unsafe_allow_html=True)
c5, c6, c7, c8 = st.columns(4)
for col, (val, label) in zip(
    [c5, c6, c7, c8],
    [
        (total_visitors_month, "Visitors (30 days)"),
        (total_routes, "Bus Routes"),
        (len(library), "Library Transactions"),
        (int(library['Return_Date'].isna().sum()), "Books Currently Issued"),
    ]
):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-label">Finance</div>', unsafe_allow_html=True)
c9, c10, c11 = st.columns(3)
for col, (val, label) in zip(
    [c9, c10, c11],
    [
        (f"₹{total_collected/100000:.2f}L", "Fees Collected"),
        (f"₹{pending_fees_amount/100000:.2f}L", "Fees Pending"),
        (f"{collection_rate:.1f}%", "Collection Rate"),
    ]
):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)