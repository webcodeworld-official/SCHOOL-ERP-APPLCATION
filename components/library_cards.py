import streamlit as st
from datetime import date


def show_library_cards(df):

    total_transactions = len(df)
    currently_issued = df["Return_Date"].isna().sum()

    today = date.today()
    overdue = df[
        df["Return_Date"].isna()
        & (df["Due_Date"].apply(lambda d: date.fromisoformat(str(d)) < today))
    ].shape[0]

    total_fine_collected = df["Fine"].fillna(0).sum()

    st.markdown('<div class="section-label">Library Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total_transactions, "📚 Total Transactions"),
        (currently_issued, "📕 Currently Issued"),
        (overdue, "⏰ Overdue"),
        (f"₹{int(total_fine_collected)}", "💰 Fine Collected"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)