from database.connection import get_connection
import pandas as pd
from datetime import date


LEAVE_TYPES = ["Casual Leave", "Sick Leave", "Earned Leave", "Unpaid Leave"]


def get_staff_by_id(staff_id):
    """Looks up a staff member by their Staff_ID, to confirm identity before submitting a request."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Staff_ID, Employee_Name, Department, Designation, Status, Branch_ID FROM staff WHERE Staff_ID = ?",
        (staff_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None
    return {
        "Staff_ID": row[0], "Employee_Name": row[1], "Department": row[2],
        "Designation": row[3], "Status": row[4], "Branch_ID": row[5],
    }


def get_next_leave_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Leave_ID) FROM leave_requests")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def submit_leave_request(staff_id, leave_type, start_date, end_date, reason, branch_id):
    conn = get_connection()
    cursor = conn.cursor()
    leave_id = get_next_leave_id()

    cursor.execute("""
        INSERT INTO leave_requests
        (Leave_ID, Staff_ID, Leave_Type, Start_Date, End_Date, Reason, Status, Applied_Date, Branch_ID)
        VALUES (?,?,?,?,?,?,'Pending',?,?)
    """, (leave_id, staff_id, leave_type, start_date, end_date, reason, date.today().isoformat(), branch_id))

    conn.commit()
    conn.close()
    return leave_id


def get_all_leave_requests(branch_id=None):
    """Returns leave requests joined with staff name/department for display."""
    conn = get_connection()
    query = """
        SELECT lr.Leave_ID, lr.Staff_ID, st.Employee_Name, st.Department,
               lr.Leave_Type, lr.Start_Date, lr.End_Date, lr.Reason,
               lr.Status, lr.Applied_Date, lr.Reviewed_By, lr.Review_Note
        FROM leave_requests lr
        JOIN staff st ON lr.Staff_ID = st.Staff_ID
    """
    if branch_id is None:
        df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query + " WHERE lr.Branch_ID = ?", conn, params=(branch_id,))
    conn.close()
    return df


def review_leave_request(leave_id, new_status, reviewed_by, review_note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leave_requests
        SET Status = ?, Reviewed_By = ?, Review_Note = ?
        WHERE Leave_ID = ?
    """, (new_status, reviewed_by, review_note, leave_id))
    conn.commit()
    conn.close()


def delete_leave_request(leave_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leave_requests WHERE Leave_ID = ?", (int(leave_id),))
    conn.commit()
    conn.close()

def get_staff_departments(branch_id=None):
    conn = get_connection()
    query = "SELECT DISTINCT Department FROM staff WHERE Status = 'Active'"
    if branch_id is None:
        df = pd.read_sql(query + " ORDER BY Department", conn)
    else:
        df = pd.read_sql(query + " AND Branch_ID = ? ORDER BY Department", conn, params=(branch_id,))
    conn.close()
    return df["Department"].tolist()


def get_designations_for_department(department, branch_id=None):
    conn = get_connection()
    query = "SELECT DISTINCT Designation FROM staff WHERE Status = 'Active' AND Department = ?"
    params = [department]
    if branch_id is not None:
        query += " AND Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY Designation"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df["Designation"].tolist()


def get_staff_for_dept_designation(department, designation, branch_id=None):
    conn = get_connection()
    query = """
        SELECT Staff_ID, Employee_Name FROM staff
        WHERE Status = 'Active' AND Department = ? AND Designation = ?
    """
    params = [department, designation]
    if branch_id is not None:
        query += " AND Branch_ID = ?"
        params.append(branch_id)
    query += " ORDER BY Employee_Name"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df