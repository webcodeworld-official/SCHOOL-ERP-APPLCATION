from database.connection import get_connection
import pandas as pd


def get_all_visitors():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM visitors", conn)
    conn.close()
    return df


def get_next_visitor_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(Visitor_ID AS INTEGER)) FROM visitors")
    result = cursor.fetchone()[0]
    conn.close()

    if result is None:
        return 1001
    return int(result) + 1


def generate_pass_no(visitor_id):
    """Matches existing pattern: VP + (Visitor_ID + 999), e.g. Visitor_ID 142 -> VP1141."""
    return f"VP{visitor_id + 999}"


def add_visitor(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO visitors
        (
            Visitor_ID, Visit_Date, Visitor_Name, Visitor_Type, Purpose,
            Student_ID, Staff_Name, Check_In, Check_Out, Pass_No
        )
        VALUES (?,?,?,?,?, ?,?,?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_visitor_dict(visitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visitors WHERE Visitor_ID = ?", (visitor_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_visitor(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE visitors
        SET
            Visit_Date=?, Visitor_Name=?, Visitor_Type=?, Purpose=?,
            Student_ID=?, Staff_Name=?, Check_In=?, Check_Out=?
        WHERE Visitor_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_visitor(visitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM visitors WHERE Visitor_ID=?", (int(visitor_id),))
    conn.commit()
    conn.close()