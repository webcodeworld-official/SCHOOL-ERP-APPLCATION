import streamlit as st


def show_transportation_cards(df):

    total_assigned = len(df)
    total_routes = df["Transport_ID"].nunique()
    total_revenue = df["Transport_Fee"].sum()
    avg_distance = df["Distance_KM"].mean() if not df.empty else 0

    st.markdown('<div class="section-label">Transport Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (total_assigned, "🎓 Students Using Transport"),
        (total_routes, "🚌 Active Routes"),
        (f"₹{int(total_revenue)}", "💰 Monthly Revenue"),
        (f"{avg_distance:.1f} KM", "📏 Avg Distance"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)