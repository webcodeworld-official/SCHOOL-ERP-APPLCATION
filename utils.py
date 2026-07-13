import pandas as pd
import streamlit as st


# =========================================================
# DATA LOADING
# =========================================================

from database.connection import get_connection

@st.cache_data
def load_data():

    conn = get_connection()

    data = {
        "STUDENT": pd.read_sql("SELECT * FROM student", conn),
        "STAFF": pd.read_sql("SELECT * FROM staff", conn),
        "VISITORS": pd.read_sql("SELECT * FROM visitors", conn),
        "TRANSPORTATION": pd.read_sql("SELECT * FROM transportation", conn),
        "LIBRARY": pd.read_sql("SELECT * FROM library", conn),
        "FEES": pd.read_sql("SELECT * FROM fees", conn),
        "ATTENDENCE": pd.read_sql("SELECT * FROM attendence", conn),
        "EXAMINATION": pd.read_sql("SELECT * FROM examination", conn),
        "ADMISSION": pd.read_sql("SELECT * FROM admission", conn)
    }

    conn.close()

    return data


# =========================================================
# SIDEBAR FILTERS
# =========================================================

def sidebar_multiselect(df, column, label=None):
    """
    Render a sidebar multiselect for a given column and
    return the selected values. Safely skips columns that
    don't exist so pages don't crash on schema drift.
    """
    if column not in df.columns:
        return []

    options = sorted(df[column].dropna().unique())
    return st.sidebar.multiselect(label or column, options)


def apply_filters(df, filters: dict):
    """
    filters = {"Class": selected_class, "Gender": selected_gender, ...}
    Applies isin() filtering for every non-empty selection.
    """
    filtered = df.copy()
    for column, values in filters.items():
        if values:
            filtered = filtered[filtered[column].isin(values)]
    return filtered


def sidebar_filter_block(df, columns: dict):
    """
    columns = {"Class": "Class", "Gender": "Gender"}  (column -> label)
    Renders a multiselect for each and returns the filtered dataframe.
    Combines sidebar_multiselect + apply_filters in one call.

    Example:
        filtered = sidebar_filter_block(
            students,
            {"Class": "Class", "Gender": "Gender"}
        )
    """
    selections = {}
    for column, label in columns.items():
        selections[column] = sidebar_multiselect(df, column, label)

    return apply_filters(df, selections)


def guard_empty(df, message="No records match the selected filters."):
    """
    Stop page execution cleanly if the filtered dataframe is empty,
    instead of letting downstream .mean()/plotly calls throw errors.
    Call this immediately after filtering, before KPIs/charts.
    """
    st.caption(f"📄 {len(df):,} records match current filters")

    if len(df) == 0:
        st.warning(f"⚠️ {message}")
        st.stop()


# =========================================================
# KPI CARDS
# =========================================================

def kpi_row(items):
    """
    items = [
        ("👨‍🎓 Total Students", len(filtered)),
        ("👦 Boys", boys_count),
        ("👧 Girls", girls_count),
        ("🏫 Classes", filtered["Class"].nunique()),
    ]
    Renders an evenly spaced row of st.metric cards.
    """
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


# =========================================================
# FORMATTING
# =========================================================

def format_currency(amount, always_lakh_above=100000):
    """
    Consistent ₹ formatting across all pages.
    Below the threshold: ₹12,340
    At/above the threshold: ₹1.23 L
    """
    if amount is None or pd.isna(amount):
        return "₹0"

    if amount >= always_lakh_above:
        return f"₹ {amount / 100000:.2f} L"

    return f"₹{amount:,.0f}"


# =========================================================
# CHARTS
# =========================================================

def chart_with_insight(fig, insight_text, box=st.success, key=None):
    """
    Renders a plotly chart followed by a styled insight callout,
    so every page uses the same wrapper instead of repeating
    st.plotly_chart(...) + st.success("Insight: ...") everywhere.
    """
    st.plotly_chart(fig, use_container_width=True, key=key)
    box(f"💡 Insight: {insight_text}")


# =========================================================
# EXPORT
# =========================================================

def download_button(df, filename="filtered_data.csv", label="⬇️ Download Filtered Data"):
    """
    Adds a CSV download button for the currently filtered dataframe.
    Drop this near the top or bottom of any page.
    """
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
    )
