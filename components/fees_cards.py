import streamlit as st


def show_fees_cards(df):

    total_due = df["Total_Fee"].sum()
    total_collected = df["Amount_Paid"].sum()
    total_pending = df["Balance"].sum()
    collection_rate = (total_collected / total_due * 100) if total_due > 0 else 0

    st.markdown('<div class="section-label">Fees Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (f"₹{int(total_due):,}", "📄 Total Due"),
        (f"₹{int(total_collected):,}", "✅ Collected"),
        (f"₹{int(total_pending):,}", "⏳ Pending"),
        (f"{collection_rate:.1f}%", "📊 Collection Rate"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)