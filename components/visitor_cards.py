import streamlit as st


def show_visitor_cards(df):

    total_visits = len(df)
    parents = (df["Visitor_Type"] == "Parent").sum()
    vendors = (df["Visitor_Type"] == "Vendor").sum()
    guests = (df["Visitor_Type"] == "Guest").sum()

    st.markdown('<div class="section-label">Visitor Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total_visits, "🚶 Total Visits"),
        (parents, "👨‍👩‍👧 Parents"),
        (vendors, "📦 Vendors"),
        (guests, "👤 Guests"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)