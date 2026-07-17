import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button
import pandas as pd
import plotly.express as px
from utils import load_custom_css
load_custom_css()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = load_data()

staff = data["STAFF"].copy()

staff["Joining_Date"] = pd.to_datetime(staff["Joining_Date"])

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("👨‍🏫 Staff Dashboard")
st.caption("Comprehensive Analysis of School Staff")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Staff")

filtered = sidebar_filter_block(
    staff,
    {
        "Department": "Department",
        "Gender": "Gender",
        "Designation": "Designation",
        "Status": "Status",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No staff records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "staff_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

kpi_row([
    ("👨‍🏫 Total Staff", len(filtered)),
    ("👨 Male", filtered[filtered["Gender"] == "Male"].shape[0]),
    ("👩 Female", filtered[filtered["Gender"] == "Female"].shape[0]),
    ("🏢 Departments", filtered["Department"].nunique()),
])

st.divider()

# --------------------------------------------------
# ROW 1
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    dept = filtered["Department"].value_counts().reset_index()
    dept.columns = ["Department", "Count"]

    fig = px.bar(
        dept,
        x="Department",
        y="Count",
        color="Count",
        text="Count",
        title="Staff by Department"
    )

    fig.update_layout(xaxis_title="", yaxis_title="Staff")

    chart_with_insight(
        fig,
        "This chart shows the number of employees in each department. Departments with more staff generally require greater coordination and resource planning.",
        box=st.info
    )

with col2:

    gender_df = filtered["Gender"].value_counts().reset_index()
    gender_df.columns = ["Gender", "Count"]

    fig = px.pie(
        gender_df,
        names="Gender",
        values="Count",
        hole=0.5,
        title="Gender Distribution"
    )

    chart_with_insight(
        fig,
        "This chart compares the proportion of male and female staff members, helping assess workforce diversity.",
        box=st.info
    )

# --------------------------------------------------
# ROW 2
# --------------------------------------------------

col3, col4 = st.columns(2)

with col3:

    desig = filtered["Designation"].value_counts().reset_index()
    desig.columns = ["Designation", "Count"]

    fig = px.bar(
        desig,
        x="Count",
        y="Designation",
        orientation="h",
        color="Count",
        text="Count",
        title="Staff by Designation"
    )

    chart_with_insight(
        fig,
        "This chart shows how staff members are distributed across different job roles within the school.",
        box=st.info
    )

with col4:

    join = (
        filtered.groupby(
            filtered["Joining_Date"].dt.to_period("Y")
        )
        .size()
        .reset_index(name="Count")
    )

    join["Joining_Date"] = join["Joining_Date"].astype(str)

    fig = px.line(
        join,
        x="Joining_Date",
        y="Count",
        markers=True,
        title="Joining Trend"
    )

    chart_with_insight(
        fig,
        "This chart shows the number of employees who joined in each year, helping identify hiring trends.",
        box=st.info
    )

# --------------------------------------------------
# ROW 3
# --------------------------------------------------

col5, col6 = st.columns(2)

with col5:

    qual = filtered["Qualification"].value_counts().reset_index()
    qual.columns = ["Qualification", "Count"]

    fig = px.bar(
        qual,
        x="Qualification",
        y="Count",
        color="Count",
        text="Count",
        title="Qualification Distribution"
    )

    chart_with_insight(
        fig,
        "This chart shows the educational qualifications of staff members. It helps understand the academic profile of the workforce.",
        box=st.info
    )

with col6:

    fig = px.histogram(
        filtered,
        x="Experience_Yrs",
        nbins=10,
        title="Experience Distribution"
    )

    chart_with_insight(
        fig,
        "This chart groups staff members based on years of experience. It helps determine whether the workforce is primarily experienced or relatively new.",
        box=st.info
    )

st.divider()
