import streamlit as st
from utils import load_data, sidebar_filter_block, guard_empty, kpi_row, chart_with_insight, download_button, format_currency
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

fees = data["FEES"].copy()
students = data["STUDENT"].copy()

# --------------------------------------------------
# CREATE STUDENT NAME
# --------------------------------------------------

students["Student_Name"] = (
    students["First_Name"].astype(str) + " " + students["Last_Name"].astype(str)
)

fees = fees.merge(
    students[["Student_ID", "Student_Name", "Class"]],
    on="Student_ID",
    how="left"
)

fees["Payment_Date"] = pd.to_datetime(fees["Payment_Date"], errors="coerce")

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("💰 Fees Dashboard")
st.caption("Monitor Fee Collection, Pending Payments and Revenue Analysis")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Fee Records")

filtered = sidebar_filter_block(
    fees,
    {
        "Month": "Month",
        "Payment_Status": "Payment Status",
        "Payment_Mode": "Payment Mode",
        "Class": "Class",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No fee records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "fees_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

total_fee = filtered["Total_Fee"].sum()
amount_paid = filtered["Amount_Paid"].sum()
balance = filtered["Balance"].sum()

collection_rate = (amount_paid / total_fee * 100) if total_fee > 0 else 0

kpi_row([
    ("💰 Total Fee", format_currency(total_fee)),
    ("✅ Fee Collected", format_currency(amount_paid)),
    ("⏳ Outstanding", format_currency(balance)),
    ("📈 Collection Rate", f"{collection_rate:.1f}%"),
])

st.divider()

# =====================================================
# CHART 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    monthly = (
        filtered.groupby("Month")["Amount_Paid"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="Month",
        y="Amount_Paid",
        markers=True,
        title="Monthly Fee Collection"
    )

    fig.update_layout(xaxis_title="Month", yaxis_title="Amount Collected (₹)")

    chart_with_insight(
        fig,
        "This chart shows how much fee was collected each month. It helps identify months with higher or lower revenue collection."
    )

with col2:

    status = (
        filtered["Payment_Status"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status", "Students"]

    fig = px.pie(
        status,
        names="Status",
        values="Students",
        hole=0.5,
        title="Payment Status Distribution"
    )

    chart_with_insight(
        fig,
        "This chart compares students who have paid their fees with those who still have pending payments."
    )

st.divider()

# =====================================================
# CHART 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    fee_components = pd.DataFrame({
        "Component": ["Tuition Fee", "Transport Fee", "Library Fee", "Exam Fee"],
        "Amount": [
            filtered["Tuition_Fee"].sum(),
            filtered["Transport_Fee"].sum(),
            filtered["Library_Fee"].sum(),
            filtered["Exam_Fee"].sum()
        ]
    })

    fig = px.bar(
        fee_components,
        x="Component",
        y="Amount",
        color="Amount",
        text_auto=".2s",
        title="Fee Component Analysis"
    )

    fig.update_layout(xaxis_title="Fee Component", yaxis_title="Amount (₹)")

    chart_with_insight(
        fig,
        "This chart compares the contribution of different fee components. Tuition fees generally account for the largest portion of school revenue."
    )

with col4:

    payment_mode = (
        filtered["Payment_Mode"]
        .value_counts()
        .reset_index()
    )

    payment_mode.columns = ["Payment Mode", "Students"]

    fig = px.pie(
        payment_mode,
        names="Payment Mode",
        values="Students",
        hole=0.45,
        title="Payment Mode Distribution"
    )

    chart_with_insight(
        fig,
        "This chart shows which payment methods are preferred by parents, helping the school understand payment trends."
    )

st.divider()

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    monthly_balance = (
        filtered.groupby("Month")["Balance"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        monthly_balance,
        x="Month",
        y="Balance",
        color="Balance",
        text_auto=".2s",
        title="Outstanding Balance by Month"
    )

    fig.update_layout(xaxis_title="Month", yaxis_title="Outstanding Balance (₹)")

    chart_with_insight(
        fig,
        "This chart highlights the unpaid fee amount each month. Larger bars indicate months where more follow-up may be needed."
    )

with col6:

    top_students = (
        filtered.groupby("Student_Name")["Amount_Paid"]
        .sum()
        .reset_index()
        .sort_values(by="Amount_Paid", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_students,
        x="Amount_Paid",
        y="Student_Name",
        orientation="h",
        color="Amount_Paid",
        text_auto=".2s",
        title="Top 10 Highest Fee Paying Students"
    )

    fig.update_layout(
        xaxis_title="Amount Paid (₹)",
        yaxis_title="Student",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=500
    )

    chart_with_insight(
        fig,
        "This chart ranks students by the total fee amount they have paid, helping identify the highest fee contributors."
    )

st.divider()
