import pandas as pd
import streamlit as st
import re

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
        ...
    ]
    Renders KPI cards styled to match the rest of the app.
    """
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

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
    Renders a plotly chart (dark-themed) followed by a styled insight callout.
    """
    apply_dark_theme(fig)
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

def is_valid_phone(phone):
    """Valid Indian mobile: exactly 10 digits, starts with 6-9."""
    return bool(re.fullmatch(r"[6-9]\d{9}", str(phone).strip()))

def is_valid_email(email):
    """Basic email format check."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(email).strip()))

import hashlib
import secrets

def hash_password(password, salt=None):
    """Returns (hashed_password, salt). Generates a new salt if none given."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return hashed, salt

def verify_password(password, salt, stored_hash):
    """Checks a login attempt against the stored hash+salt."""
    check_hash, _ = hash_password(password, salt)
    return check_hash == stored_hash

from pathlib import Path
import streamlit as st

def load_custom_css():
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def apply_dark_theme(fig):
    """Applies the app's dark theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#27272A",
        plot_bgcolor="#27272A",
        font_color="#FAFAFA",
        title_font_color="#FAFAFA",
        legend_font_color="#FAFAFA",
        xaxis=dict(gridcolor="#3F3F46", color="#A1A1AA"),
        yaxis=dict(gridcolor="#3F3F46", color="#A1A1AA"),
        margin=dict(t=50, b=30, l=30, r=30),
    )
    return fig
