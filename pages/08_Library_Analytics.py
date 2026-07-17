import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button, format_currency
import pandas as pd
import plotly.express as px
from utils import load_custom_css
load_custom_css()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = load_data()

library = data["LIBRARY"].copy()
students = data["STUDENT"].copy()

# --------------------------------------------------
# CREATE STUDENT NAME
# --------------------------------------------------

students["Student_Name"] = (
    students["First_Name"].astype(str) + " " + students["Last_Name"].astype(str)
)

library = library.merge(
    students[["Student_ID", "Student_Name", "Class"]],
    on="Student_ID",
    how="left"
)

# --------------------------------------------------
# DATE CONVERSION
# --------------------------------------------------

library["Issue_Date"] = pd.to_datetime(library["Issue_Date"], errors="coerce")
library["Due_Date"] = pd.to_datetime(library["Due_Date"], errors="coerce")
library["Return_Date"] = pd.to_datetime(library["Return_Date"], errors="coerce")

library["Month"] = library["Issue_Date"].dt.strftime("%b-%Y")

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("📚 Library Dashboard")
st.caption("Monitor Book Issues, Returns, Library Usage and Fine Collection")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Library Records")

filtered = sidebar_filter_block(
    library,
    {
        "Month": "Issue Month",
        "Book_Name": "Book Name",
        "Class": "Class",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No library records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "library_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

kpi_row([
    ("📚 Books Issued", len(filtered)),
    ("👨‍🎓 Students", filtered["Student_ID"].nunique()),
    ("📖 Unique Books", filtered["Book_Name"].nunique()),
    ("💰 Fine Collected", format_currency(filtered["Fine"].sum())),
])

st.divider()

# =====================================================
# CHART 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    monthly_issue = (
        filtered.groupby("Month")
        .size()
        .reset_index(name="Books Issued")
    )

    fig = px.line(
        monthly_issue,
        x="Month",
        y="Books Issued",
        markers=True,
        title="Monthly Book Issue Trend"
    )

    fig.update_layout(xaxis_title="Month", yaxis_title="Books Issued")

    chart_with_insight(
        fig,
        "This chart shows the number of books issued every month. It helps identify periods when library usage is highest."
    )

with col2:

    top_books = (
        filtered["Book_Name"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_books.columns = ["Book", "Issues"]

    fig = px.bar(
        top_books,
        x="Issues",
        y="Book",
        orientation="h",
        color="Issues",
        text="Issues",
        title="Top 10 Most Borrowed Books"
    )

    fig.update_layout(
        xaxis_title="Times Issued",
        yaxis_title="Book Name",
        yaxis=dict(autorange="reversed")
    )

    chart_with_insight(
        fig,
        "This chart highlights the books that are borrowed most frequently, helping the library identify popular titles."
    )

st.divider()

# =====================================================
# CHART 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    fine_book = (
        filtered.groupby("Book_Name")["Fine"]
        .sum()
        .reset_index()
        .sort_values(by="Fine", ascending=False)
        .head(10)
    )

    fig = px.bar(
        fine_book,
        x="Book_Name",
        y="Fine",
        color="Fine",
        text_auto=".2s",
        title="Top 10 Books Generating Fine"
    )

    fig.update_layout(xaxis_title="Book Name", yaxis_title="Fine Collected (₹)")

    chart_with_insight(
        fig,
        "This chart shows which books generated the highest fines. It helps identify books that are frequently returned late."
    )

with col4:

    issue_distribution = (
        filtered["Book_Name"]
        .value_counts()
        .head(8)
        .reset_index()
    )

    issue_distribution.columns = ["Book", "Issues"]

    fig = px.pie(
        issue_distribution,
        names="Book",
        values="Issues",
        hole=0.45,
        title="Book Issue Distribution"
    )

    chart_with_insight(
        fig,
        "This chart shows how book issues are distributed among the most borrowed books, helping identify reader preferences."
    )

st.divider()

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    daily_issue = (
        filtered.groupby("Issue_Date")
        .size()
        .reset_index(name="Books Issued")
    )

    fig = px.area(
        daily_issue,
        x="Issue_Date",
        y="Books Issued",
        title="Daily Book Issue Trend"
    )

    fig.update_layout(xaxis_title="Issue Date", yaxis_title="Books Issued")

    chart_with_insight(
        fig,
        "This chart tracks daily library activity. Peaks indicate days when more students borrowed books."
    )

with col6:

    top_students = (
        filtered.groupby("Student_Name")
        .size()
        .reset_index(name="Books Issued")
        .sort_values(by="Books Issued", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_students,
        x="Books Issued",
        y="Student_Name",
        orientation="h",
        color="Books Issued",
        text="Books Issued",
        title="Top 10 Library Users"
    )

    fig.update_layout(
        xaxis_title="Books Issued",
        yaxis_title="Student",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=500
    )

    chart_with_insight(
        fig,
        "This chart identifies the students who borrow books most frequently, reflecting active library usage."
    )

st.divider()
