import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from utils import load_data
from datetime import datetime

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------

st.set_page_config(
    page_title="School ERP Analytics Dashboard",
    page_icon="🏫",
    layout="wide"
)

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

data = load_data()

students = data["STUDENT"]
staff = data["STAFF"]
visitors = data["VISITORS"]
transport = data["TRANSPORTATION"]
library = data["LIBRARY"]
fees = data["FEES"]
attendance = data["ATTENDENCE"]
exam = data["EXAMINATION"]

# -------------------------------------------------------
# KPI VALUES
# -------------------------------------------------------

total_students = len(students)
total_staff = len(staff)
total_visitors = len(visitors)
total_buses = transport["Bus_No"].nunique()

books_issued = len(library)

total_fee = fees["Amount_Paid"].sum()

attendance_percent = (
    attendance["Status"]
    .isin(["Present", "Late"])
    .mean() * 100
)

avg_marks = exam["Percentage"].mean()

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------

st.title("🏫 School ERP Analytics Dashboard")

today = datetime.now()

col1, col2 = st.columns([1,1])

with col1:
    st.write(f"📅 **Date :** {today.strftime('%d %B %Y')}")

with col2:
    st.write(f"🕒 **Time :** {today.strftime('%I:%M %p')}")

st.divider()

# -------------------------------------------------------
# KPI ROW 1
# -------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("👨‍🎓 Students", total_students)
c2.metric("👩‍🏫 Staff", total_staff)
c3.metric("🚶 Visitors", total_visitors)
c4.metric("🚌 Buses", total_buses)

style_metric_cards(
    background_color="#1E293B",
    border_left_color="#2563EB",
    border_color="#334155"
)

st.write("")

# -------------------------------------------------------
# KPI ROW 2
# -------------------------------------------------------

c5, c6, c7, c8 = st.columns(4)

c5.metric("📚 Books Issued", books_issued)

c6.metric(
    "💰 Fee Collection",
    f"₹ {total_fee/100000:.2f} L"
)

c7.metric(
    "📅 Attendance",
    f"{attendance_percent:.1f}%"
)

c8.metric(
    "📝 Avg Percentage",
    f"{avg_marks:.1f}%"
)

style_metric_cards(
    background_color="#1E293B",
    border_left_color="#16A34A",
    border_color="#334155"
)

st.divider()

# -------------------------------------------------------
# WELCOME
# -------------------------------------------------------

st.subheader("Welcome 👋")

st.info(
"""
#### MODULES INCLUDED:
🎓 Students

👩‍🏫 Staff

🚶 Visitors

🚌 Transportation

📚 Library

💰 Fees

📅 Attendance

📝 Examination

📥 Admission
"""
)