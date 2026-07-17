import streamlit as st
from database.transportation_queries import get_distinct_routes, get_unassigned_students, get_next_route_number, FEE_PER_KM


def transportation_form(record=None, routes_df=None, unassigned_df=None):
    """
    Reusable Transportation Assignment Form.

    If record=None -> Assign a student to transport (new row)
    If record has data -> Edit an existing assignment

    routes_df / unassigned_df are passed in so the dialog only queries the DB once.

    Returns dictionary containing all entered values.
    """

    if record is None:
        record = {}

    key_suffix = str(record.get("Student_ID", "new"))
    is_edit = "Student_ID" in record and record.get("Student_ID") is not None

    col1, col2 = st.columns(2)

    with col1:
        if is_edit:
            student_id = record["Student_ID"]
            st.text_input("Student ID", value=str(student_id), disabled=True, key=f"sid_{key_suffix}")
        else:
            if unassigned_df is None or unassigned_df.empty:
                st.warning("No unassigned active students available.")
                student_id = None
            else:
                options = unassigned_df.apply(
                    lambda r: f"{r['Student_ID']} - {r['First_Name']} {r['Last_Name']} (Class {r['Class']}{r['Section']})",
                    axis=1
                ).tolist()
                choice = st.selectbox("Student", options, key=f"student_pick_{key_suffix}")
                student_id = int(choice.split(" - ")[0])

        # Route picker: choose an existing route, or "New Route"
        route_labels = ["+ New Route"]
        route_lookup = {}
        if routes_df is not None and not routes_df.empty:
            for _, r in routes_df.iterrows():
                label = f"Route {r['Transport_ID']} - {r['Bus_No']} ({r['Route']})"
                route_labels.append(label)
                route_lookup[label] = r

        current_route_label = None
        if is_edit and routes_df is not None:
            match = routes_df[routes_df["Transport_ID"] == record.get("Transport_ID")]
            if not match.empty:
                r = match.iloc[0]
                current_route_label = f"Route {r['Transport_ID']} - {r['Bus_No']} ({r['Route']})"

        default_index = route_labels.index(current_route_label) if current_route_label in route_labels else 0

        selected_route_label = st.selectbox(
            "Route",
            route_labels,
            index=default_index,
            key=f"route_pick_{key_suffix}"
        )

    with col2:
        if selected_route_label == "+ New Route":
            transport_id = get_next_route_number()
            bus_no = st.text_input("Bus No", value=f"BUS-{transport_id}", key=f"bus_{key_suffix}")
            route_name = st.text_input("Route", value="", key=f"route_name_{key_suffix}")
            driver = st.text_input("Driver", value="", key=f"driver_{key_suffix}")
            driver_phone = st.text_input("Driver Phone", value="", key=f"driver_phone_{key_suffix}")
            distance_km = st.number_input("Distance (KM)", min_value=1, value=10, key=f"distance_{key_suffix}")
        else:
            route = route_lookup[selected_route_label]
            transport_id = int(route["Transport_ID"])
            bus_no = route["Bus_No"]
            route_name = route["Route"]
            driver = route["Driver"]
            driver_phone = str(route["Driver_Phone"])
            distance_km = int(route["Distance_KM"])

            st.text_input("Bus No", value=bus_no, disabled=True, key=f"bus_ro_{key_suffix}")
            st.text_input("Driver", value=driver, disabled=True, key=f"driver_ro_{key_suffix}")
            st.caption(f"Distance: {distance_km} KM | Route: {route_name}")

        pickup_point = st.text_input(
            "Pickup Point",
            value=record.get("Pickup_Point", ""),
            key=f"pickup_{key_suffix}"
        )

        suggested_fee = distance_km * FEE_PER_KM
        transport_fee = st.number_input(
            "Transport Fee",
            min_value=0,
            value=int(record.get("Transport_Fee", suggested_fee)),
            key=f"fee_{key_suffix}"
        )

    return {
        "Student_ID": student_id,
        "Transport_ID": transport_id,
        "Bus_No": bus_no,
        "Route": route_name,
        "Pickup_Point": pickup_point,
        "Driver": driver,
        "Driver_Phone": driver_phone,
        "Distance_KM": distance_km,
        "Transport_Fee": transport_fee,
    }
