import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button
import pandas as pd
import plotly.express as px
from utils import load_custom_css
load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()
# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

data = load_data()

students = data["STUDENT"].copy()

# -------------------------------------------------------
# DATE CONVERSION
# -------------------------------------------------------

students["Admission_Date"] = pd.to_datetime(students["Admission_Date"])
students["Date_of_Birth"] = pd.to_datetime(students["Date_of_Birth"])

today = pd.Timestamp.today()

students["Age"] = (
    (today - students["Date_of_Birth"]).dt.days // 365
)

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("🎓 Students Dashboard")
st.caption("Comprehensive Analysis of Student Information")

st.divider()

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------

st.sidebar.header("Filter Students")

filtered = sidebar_filter_block(
    students,
    {"Class": "Class", "Gender": "Gender"}
)

# -------------------------------------------------------
# EMPTY-STATE GUARD
# -------------------------------------------------------

guard_empty(filtered, "No students match the selected filters.")

# -------------------------------------------------------
# DOWNLOAD
# -------------------------------------------------------

download_button(filtered, "students_filtered.csv")

# -------------------------------------------------------
# KPI CARDS
# -------------------------------------------------------

kpi_row([
    ("👨‍🎓 Total Students", len(filtered)),
    ("👦 Boys", filtered[filtered["Gender"] == "Male"].shape[0]),
    ("👧 Girls", filtered[filtered["Gender"] == "Female"].shape[0]),
    ("🏫 Classes", filtered["Class"].nunique()),
])

st.divider()

# =====================================================
# CHART 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    class_count = filtered["Class"].value_counts().sort_index()

    fig = px.bar(
        x=class_count.index,
        y=class_count.values,
        color=class_count.values,
        text=class_count.values,
        title="Students by Class",
        labels={"x": "Class", "y": "Students"}
    )

    chart_with_insight(
        fig,
        "This chart shows the number of students in each class. Classes with taller bars have more students, helping the school identify where additional teachers or classrooms may be required."
    )

with col2:

    gender = filtered["Gender"].value_counts()

    fig = px.pie(
        values=gender.values,
        names=gender.index,
        hole=.45,
        title="Gender Distribution"
    )

    chart_with_insight(
        fig,
        "This chart compares the number of male and female students. It helps understand whether the student population is balanced across genders."
    )

# =====================================================
# CHART 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    admission = filtered.groupby(
        filtered["Admission_Date"].dt.to_period("M")
    ).size()

    admission.index = admission.index.astype(str)

    fig = px.line(
        x=admission.index,
        y=admission.values,
        markers=True,
        title="Monthly Admission Trend",
        labels={"x": "Month", "y": "Admissions"}
    )

    chart_with_insight(
        fig,
        "This chart shows how student admissions changed over time. Peaks indicate months with higher admissions and help identify seasonal enrollment trends."
    )

with col4:

    house = filtered["House"].value_counts()

    fig = px.pie(
        values=house.values,
        names=house.index,
        hole=.6,
        title="House Distribution"
    )

    chart_with_insight(
        fig,
        "Students are grouped into different houses. This chart shows whether students are evenly distributed among the houses."
    )

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    fig = px.histogram(
        filtered,
        x="Age",
        nbins=12,
        title="Age Distribution"
    )

    chart_with_insight(
        fig,
        "This chart groups students according to their age. It helps identify the most common age groups within the school."
    )

with col6:

    city = (
        filtered["City"]
        .value_counts()
        .reset_index()
    )

    city.columns = ["City", "Students"]

    fig = px.treemap(
        city,
        path=["City"],
        values="Students",
        title="Students by City"
    )

    chart_with_insight(
        fig,
        "This chart shows which cities contribute the highest number of students. Larger rectangles represent cities with more enrolled students, helping the school understand its geographic reach."
    )

st.divider()
