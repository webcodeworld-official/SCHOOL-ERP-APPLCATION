import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button, format_currency
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Admission Dashboard",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = load_data()

admission = data["ADMISSION"].copy()

# Convert date column
admission["Admission_Date"] = pd.to_datetime(
    admission["Admission_Date"],
    errors="coerce"
)

# Create Month-Year column from Admission_Date
admission["Month"] = admission["Admission_Date"].dt.strftime("%b-%Y")

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎓 Admission Dashboard")
st.caption("Monitor Admissions, Fees and Student Enrollment")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Admissions")

filtered = sidebar_filter_block(
    admission,
    {
        "Admission_Status": "Admission Status",
        "Entrance_Test": "Entrance Test",
        "Month": "Admission Month",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No admission records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "admissions_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

kpi_row([
    ("🎓 Total Applications", len(filtered)),
    ("✅ Approved", filtered[filtered["Admission_Status"] == "Approved"].shape[0]),
    ("⌛ Pending", filtered[filtered["Admission_Status"] == "Pending"].shape[0]),
    ("💰 Admission Fee", format_currency(filtered["Admission_Fee"].sum())),
])

st.divider()

# =====================================================
# CHART 1 - Admissions by Month
# =====================================================

col1, col2 = st.columns(2)

with col1:

    month = (
        filtered["Month"]
        .value_counts()
        .reset_index()
    )

    month.columns = ["Month", "Admissions"]

    fig = px.bar(
        month,
        x="Month",
        y="Admissions",
        color="Admissions",
        text="Admissions",
        title="Admissions by Month"
    )

    fig.update_layout(xaxis_title="Admission Month", yaxis_title="Students")

    chart_with_insight(
        fig,
        "This chart shows the number of admissions received each month, helping identify peak admission periods."
    )

with col2:

    status = (
        filtered["Admission_Status"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status", "Students"]

    fig = px.pie(
        status,
        names="Status",
        values="Students",
        hole=0.5,
        title="Admission Status Distribution"
    )

    chart_with_insight(
        fig,
        "This chart compares approved and pending admissions, helping administrators monitor the admission process."
    )

st.divider()

# =====================================================
# CHART 2 - Entrance Test Analysis
# =====================================================

col3, col4 = st.columns(2)

with col3:

    entrance = (
        filtered["Entrance_Test"]
        .value_counts()
        .reset_index()
    )

    entrance.columns = ["Result", "Students"]

    fig = px.bar(
        entrance,
        x="Result",
        y="Students",
        color="Students",
        text="Students",
        title="Entrance Test Result"
    )

    chart_with_insight(
        fig,
        "This chart shows how many students passed or failed the entrance test. It helps evaluate admission eligibility."
    )

with col4:

    monthly_fee = (
        filtered.groupby("Month")["Admission_Fee"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly_fee,
        x="Month",
        y="Admission_Fee",
        markers=True,
        title="Admission Fee Collected by Month"
    )

    fig.update_layout(xaxis_title="Month", yaxis_title="Admission Fee (₹)")

    chart_with_insight(
        fig,
        "This chart shows the admission fee collected each month, making it easy to identify months with higher enrollment revenue."
    )

st.divider()

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    previous_school = (
        filtered["Previous_School"]
        .value_counts()
        .reset_index()
    )

    previous_school.columns = ["Previous School", "Students"]

    fig = px.bar(
        previous_school,
        x="Previous School",
        y="Students",
        color="Students",
        text="Students",
        title="Students by Previous School"
    )

    chart_with_insight(
        fig,
        "This chart shows which previous schools contribute the most admissions. It helps understand the school's primary feeder institutions."
    )
