from database.connection import get_connection
import pandas as pd

FEE_PER_KM = 60  # used to suggest a fee when assigning a new route


def get_all_transportation():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM transportation", conn)
    conn.close()
    return df


def get_distinct_routes():
    """Returns one row per unique Transport_ID with its shared route details,
    used to populate the route-picker dropdown when assigning a student."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT Transport_ID, Bus_No, Route, Driver, Driver_Phone, Distance_KM
        FROM transportation
        GROUP BY Transport_ID
    """, conn)
    conn.close()
    return df


def get_unassigned_students():
    """Active students who don't currently have a transport assignment."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT Student_ID, First_Name, Last_Name, Class, Section
        FROM student
        WHERE Status = 'Active'
        AND Student_ID NOT IN (SELECT Student_ID FROM transportation)
    """, conn)
    conn.close()
    return df


def add_transportation_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transportation
        (Transport_ID, Student_ID, Bus_No, Route, Pickup_Point, Driver, Driver_Phone, Distance_KM, Transport_Fee)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_transportation_dict(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transportation WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_transportation_record(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transportation
        SET Transport_ID=?, Bus_No=?, Route=?, Pickup_Point=?, Driver=?,
            Driver_Phone=?, Distance_KM=?, Transport_Fee=?
        WHERE Student_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_transportation_record(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transportation WHERE Student_ID=?", (int(student_id),))
    conn.commit()
    conn.close()


def get_next_route_number():
    """For creating a brand new route (not just assigning to an existing one)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Transport_ID) FROM transportation")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def sync_student_transport_id(student_id, transport_id):
    """Keeps student.Transport_ID in sync after an assignment is added/changed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student SET Transport_ID = ? WHERE Student_ID = ?",
        (transport_id, student_id)
    )
    conn.commit()
    conn.close()


def clear_student_transport_id(student_id):
    """Keeps student.Transport_ID in sync after an assignment is removed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student SET Transport_ID = NULL WHERE Student_ID = ?",
        (student_id,)
    )
    conn.commit()
    conn.close()
