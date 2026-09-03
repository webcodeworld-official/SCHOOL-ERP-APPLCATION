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

exam_df = data["EXAMINATION"].copy()
student_df = data["STUDENT"].copy()

# --------------------------------------------------
# CREATE STUDENT NAME
# --------------------------------------------------

student_df["Student_Name"] = (
    student_df["First_Name"].astype(str) + " " +
    student_df["Last_Name"].astype(str)
)

exam_df = exam_df.merge(
    student_df[["Student_ID", "Student_Name"]],
    on="Student_ID",
    how="left"
)

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

col_title, col_refresh = st.columns([5, 1])
with col_title:
    st.title("📚 Examination Dashboard")
    st.caption("Analyze Student Performance, Grades, Marks and Examination Results")
with col_refresh:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True, key="refresh_examination"):
        load_data.clear()
        st.rerun()
st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Examination Data")

filtered = sidebar_filter_block(
    exam_df,
    {
        "Exam_Name": "Exam Name",
        "Subject": "Subject",
        "Grade": "Grade",
        "Result": "Result",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No examination records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "examination_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

pass_rate = (
    (filtered["Result"] == "Pass").sum() / len(filtered) * 100
    if len(filtered) > 0 else 0
)

kpi_row([
    ("👨‍🎓 Students Appeared", filtered["Student_ID"].nunique()),
    ("📚 Subjects", filtered["Subject"].nunique()),
    ("🏆 Average %", f"{filtered['Percentage'].mean():.1f}%"),
    ("✅ Pass Rate", f"{pass_rate:.1f}%"),
])

st.divider()

# =====================================================
# CHART 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    subject_marks = (
        filtered.groupby("Subject")["Marks_Obtained"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        subject_marks,
        x="Subject",
        y="Marks_Obtained",
        color="Marks_Obtained",
        text_auto=".1f",
        title="Average Marks by Subject"
    )

    fig.update_layout(xaxis_title="Subject", yaxis_title="Average Marks")

    chart_with_insight(
        fig,
        "This chart compares the average marks scored in each subject. Lower average marks may indicate subjects where students need additional academic support."
    )

with col2:

    result_data = (
        filtered["Result"]
        .value_counts()
        .reset_index()
    )

    result_data.columns = ["Result", "Students"]

    fig = px.pie(
        result_data,
        names="Result",
        values="Students",
        hole=0.5,
        title="Pass vs Fail Distribution"
    )

    chart_with_insight(
        fig,
        "This chart shows the proportion of students who passed and failed. It provides an overview of overall examination performance."
    )

st.divider()

# =====================================================
# CHART 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    grade_data = (
        filtered["Grade"]
        .value_counts()
        .reset_index()
    )

    grade_data.columns = ["Grade", "Students"]

    fig = px.pie(
        grade_data,
        names="Grade",
        values="Students",
        hole=0.45,
        title="Grade Distribution"
    )

    chart_with_insight(
        fig,
        "This chart shows how students are distributed across different grades. A higher number of A and B grades indicates stronger academic performance."
    )

with col4:

    subject_percentage = (
        filtered.groupby("Subject")["Percentage"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        subject_percentage,
        x="Subject",
        y="Percentage",
        color="Percentage",
        text_auto=".1f",
        title="Average Percentage by Subject"
    )

    fig.update_layout(xaxis_title="Subject", yaxis_title="Average Percentage (%)")

    chart_with_insight(
        fig,
        "This chart compares the average percentage scored in each subject. Subjects with lower averages may require additional attention."
    )

st.divider()

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    fig = px.histogram(
        filtered,
        x="Percentage",
        nbins=10,
        color="Grade",
        title="Percentage Distribution"
    )

    fig.update_layout(xaxis_title="Percentage (%)", yaxis_title="Number of Records")

    chart_with_insight(
        fig,
        "This histogram shows how student percentages are distributed. It helps identify whether most students scored high, average, or low marks."
    )

with col6:

    top_students = (
        filtered.groupby(["Student_ID", "Student_Name"])["Percentage"]
        .mean()
        .reset_index()
        .sort_values(by="Percentage", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_students,
        x="Percentage",
        y="Student_Name",
        orientation="h",
        color="Percentage",
        text_auto=".1f",
        title="🏆 Top 10 Student Performers"
    )

    fig.update_layout(
        xaxis_title="Average Percentage (%)",
        yaxis_title="Student Name",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=500
    )

    chart_with_insight(
        fig,
        "This chart ranks the top 10 students based on their average percentage across all subjects, making it easy to recognize outstanding performers."
    )

st.divider()
