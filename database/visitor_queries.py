from database.connection import get_connection
import pandas as pd


def get_all_visitors(branch_id=None):
    """Returns visitors joined with staff, so 'Meeting With' shows Name + Designation, not a raw ID."""
    conn = get_connection()
    base_query = """
        SELECT
            v.Visitor_ID, v.Visit_Date, v.Visitor_Name, v.Visitor_Type, v.Purpose,
            v.Student_ID, v.Staff_ID,
            st.Employee_Name AS Meeting_With,
            st.Designation AS Designation,
            v.Check_In, v.Check_Out, v.Pass_No, v.Branch_ID
        FROM visitors v
        LEFT JOIN staff st ON v.Staff_ID = st.Staff_ID
    """
    if branch_id is None:
        df = pd.read_sql(base_query, conn)
    else:
        df = pd.read_sql(base_query + " WHERE v.Branch_ID = ?", conn, params=(branch_id,))
    conn.close()
    return df

def get_active_staff_for_meeting(branch_id=None):
    conn = get_connection()
    if branch_id is None:
        df = pd.read_sql("""
            SELECT Staff_ID, Employee_Name, Designation
            FROM staff WHERE Status = 'Active'
            ORDER BY Employee_Name
        """, conn)
    else:
        df = pd.read_sql("""
            SELECT Staff_ID, Employee_Name, Designation
            FROM staff WHERE Status = 'Active' AND Branch_ID = ?
            ORDER BY Employee_Name
        """, conn, params=(branch_id,))
    conn.close()
    return df


def get_next_visitor_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(Visitor_ID AS INTEGER)) FROM visitors")
    result = cursor.fetchone()[0]
    conn.close()
    return 1001 if result is None else int(result) + 1


def generate_pass_no(visitor_id):
    return f"VP{visitor_id + 999}"

def add_visitor(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO visitors
        (
            Visitor_ID, Visit_Date, Visitor_Name, Visitor_Type, Purpose,
            Student_ID, Staff_ID, Check_In, Check_Out, Pass_No, Branch_ID
        )
        VALUES (?,?,?,?,?, ?,?,?,?,?,?)
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
            Student_ID=?, Staff_ID=?, Check_In=?, Check_Out=?
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
