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

transport = data["TRANSPORTATION"].copy()

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("🚌 Transportation Dashboard")
st.caption("Monitor School Transportation Routes, Students and Fees")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filter Transportation")

filtered = sidebar_filter_block(
    transport,
    {
        "Bus_No": "Bus Number",
        "Route": "Route",
        "Driver": "Driver",
    }
)

# --------------------------------------------------
# EMPTY-STATE GUARD
# --------------------------------------------------

guard_empty(filtered, "No transportation records match the selected filters.")

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

download_button(filtered, "transportation_filtered.csv")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

kpi_row([
    ("👨‍🎓 Students Using Transport", len(filtered)),
    ("🚌 Total Buses", filtered["Bus_No"].nunique()),
    ("🛣️ Total Routes", filtered["Route"].nunique()),
    ("💰 Transport Fee", format_currency(filtered["Transport_Fee"].sum())),
])

st.divider()

# =====================================================
# CHART 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    bus = (
        filtered["Bus_No"]
        .value_counts()
        .reset_index()
    )

    bus.columns = ["Bus", "Students"]

    fig = px.bar(
        bus,
        x="Bus",
        y="Students",
        color="Students",
        text="Students",
        title="Students Using Each Bus"
    )

    chart_with_insight(
        fig,
        "This chart shows how many students are assigned to each bus. It helps identify buses that are carrying more students than others."
    )

with col2:

    route = (
        filtered["Route"]
        .value_counts()
        .reset_index()
    )

    route.columns = ["Route", "Students"]

    fig = px.bar(
        route,
        x="Students",
        y="Route",
        orientation="h",
        color="Students",
        text="Students",
        title="Students by Route"
    )

    chart_with_insight(
        fig,
        "Routes with more students may require additional planning or larger vehicles to ensure efficient transportation."
    )

# =====================================================
# CHART 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    fee = (
        filtered.groupby("Bus_No")["Transport_Fee"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        fee,
        x="Bus_No",
        y="Transport_Fee",
        color="Transport_Fee",
        text="Transport_Fee",
        title="Transport Fee Collected by Bus"
    )

    chart_with_insight(
        fig,
        "This chart compares the transport fee collected from students travelling on each bus."
    )

with col4:

    route_fee = (
        filtered.groupby("Route")["Transport_Fee"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        route_fee,
        names="Route",
        values="Transport_Fee",
        hole=0.5,
        title="Fee Distribution by Route"
    )

    chart_with_insight(
        fig,
        "This chart shows which transport routes contribute the highest share of transport fee collection."
    )

# =====================================================
# CHART 3
# =====================================================

col5, col6 = st.columns(2)

with col5:

    fig = px.histogram(
        filtered,
        x="Distance_KM",
        nbins=10,
        title="Distance Travelled by Students"
    )

    chart_with_insight(
        fig,
        "This chart shows how far students travel to school. Most students usually fall within a few common distance ranges."
    )

with col6:

    driver = (
        filtered["Driver"]
        .value_counts()
        .reset_index()
    )

    driver.columns = ["Driver", "Students"]

    fig = px.bar(
        driver,
        x="Driver",
        y="Students",
        color="Students",
        text="Students",
        title="Students Assigned to Each Driver"
    )

    fig.update_layout(xaxis_title="Driver", yaxis_title="Students")

    chart_with_insight(
        fig,
        "This chart shows the number of students assigned to each driver. It helps ensure student allocation is balanced among drivers."
    )

# =====================================================
# CHART 4
# =====================================================

col7, col8 = st.columns(2)

with col7:

    pickup = (
        filtered["Pickup_Point"]
        .value_counts()
        .reset_index()
    )

    pickup.columns = ["Pickup Point", "Students"]

    fig = px.bar(
        pickup,
        x="Pickup Point",
        y="Students",
        color="Students",
        text="Students",
        title="Students by Pickup Point"
    )

    chart_with_insight(
        fig,
        "This chart shows which pickup locations have the highest number of students. It helps optimize bus stop planning."
    )

with col8:

    distance = (
        filtered.groupby("Route")["Distance_KM"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        distance,
        x="Route",
        y="Distance_KM",
        markers=True,
        title="Average Route Distance"
    )

    chart_with_insight(
        fig,
        "This chart compares the average travel distance for each route. Longer routes may require additional travel time and fuel."
    )

st.divider()
