import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button
import pandas as pd
import plotly.express as px
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = load_data()

visitors = data["VISITORS"].copy()

visitors["Visit_Date"] = pd.to_datetime(visitors["Visit_Date"])

# Convert Check-In to datetime if possible
visitors["Check_In"] = pd.to_datetime(
    visitors["Check_In"],
    errors="coerce"
)

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

col_title, col_refresh = st.columns([5, 1])
with col_title:
    st.title("🚶 Visitors Dashboard")
    st.caption("Interactive Dashboard for Visitor Management and Analysis")
with col_refresh:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True, key="refresh_visitors"):
        load_data.clear()
        st.rerun()
st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Visitors")

filtered = sidebar_filter_block(
    visitors,
    {
        "Visitor_Type": "Visitor Type",
        "Purpose": "Purpose",
        "Staff_Name": "Staff Name",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No visitor records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "visitors_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

kpi_row([
    ("🚶 Total Visitors", len(filtered)),
    ("👨‍👩‍👧 Parents", filtered[filtered["Visitor_Type"] == "Parent"].shape[0]),
    ("🚚 Vendors", filtered[filtered["Visitor_Type"] == "Vendor"].shape[0]),
    ("📋 Visitor Types", filtered["Visitor_Type"].nunique()),
])

st.divider()

# ==================================================
# CHART 1
# ==================================================

col1, col2 = st.columns(2)

with col1:

    purpose = (
        filtered["Purpose"]
        .value_counts()
        .reset_index()
    )

    purpose.columns = ["Purpose", "Visitors"]

    fig = px.bar(
        purpose,
        x="Purpose",
        y="Visitors",
        color="Visitors",
        text="Visitors",
        title="Visitors by Purpose"
    )

    fig.update_layout(xaxis_title="Purpose", yaxis_title="Visitors")

    chart_with_insight(
        fig,
        "This chart shows the main reasons visitors come to the school. It helps management identify the most common visitor activities."
    )

with col2:

    visitor_type = (
        filtered["Visitor_Type"]
        .value_counts()
        .reset_index()
    )

    visitor_type.columns = ["Type", "Count"]

    fig = px.pie(
        visitor_type,
        names="Type",
        values="Count",
        hole=0.5,
        title="Visitor Type Distribution"
    )

    chart_with_insight(
        fig,
        "This chart compares different categories of visitors such as parents and vendors. It helps understand who visits the school most frequently."
    )

# ==================================================
# CHART 2
# ==================================================

col3, col4 = st.columns(2)

with col3:

    trend = (
        filtered.groupby("Visit_Date")
        .size()
        .reset_index(name="Visitors")
    )

    fig = px.line(
        trend,
        x="Visit_Date",
        y="Visitors",
        markers=True,
        title="Daily Visitor Trend"
    )

    chart_with_insight(
        fig,
        "This chart tracks visitor activity over time. Days with higher visitor counts may require additional security and reception staff."
    )

with col4:

    staff_visit = (
        filtered["Staff_Name"]
        .value_counts()
        .reset_index()
    )

    staff_visit.columns = ["Staff", "Visitors"]

    fig = px.bar(
        staff_visit,
        x="Visitors",
        y="Staff",
        orientation="h",
        color="Visitors",
        text="Visitors",
        title="Visitors by Staff Member"
    )

    chart_with_insight(
        fig,
        "This chart shows which staff members receive the highest number of visitors, helping identify departments with greater public interaction."
    )

# ==================================================
# CHART 3
# ==================================================

col5, col6 = st.columns(2)

with col5:

    purpose_pie = (
        filtered["Purpose"]
        .value_counts()
        .reset_index()
    )

    purpose_pie.columns = ["Purpose", "Count"]

    fig = px.pie(
        purpose_pie,
        names="Purpose",
        values="Count",
        hole=0.4,
        title="Purpose Distribution"
    )

    chart_with_insight(
        fig,
        "This chart highlights the proportion of each visit purpose, allowing the school to better understand visitor needs."
    )

with col6:

    checkin = filtered.copy()
    checkin["Hour"] = checkin["Check_In"].dt.hour

    fig = px.histogram(
        checkin,
        x="Hour",
        nbins=12,
        title="Check-In Time Distribution"
    )

    fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Visitors")

    chart_with_insight(
        fig,
        "This chart shows the busiest check-in hours. It helps the school identify peak visiting times for better reception and security planning."
    )

st.divider()

# ==================================================
# MONTHLY VISITOR TREND
# ==================================================

st.subheader("📅 Monthly Visitor Trend")

monthly = (
    filtered.groupby(
        filtered["Visit_Date"].dt.to_period("M")
    )
    .size()
    .reset_index(name="Visitors")
)

monthly["Visit_Date"] = monthly["Visit_Date"].astype(str)

fig = px.area(
    monthly,
    x="Visit_Date",
    y="Visitors",
    title="Monthly Visitor Trend"
)

chart_with_insight(
    fig,
    "This chart summarizes visitor activity month by month. It helps identify seasonal trends and periods of high visitor traffic.",
    box=st.info
)

st.divider()
