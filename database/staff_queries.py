from database.connection import get_connection
import pandas as pd


def get_all_staff():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM staff", conn)
    conn.close()
    return df


def get_next_staff_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(CAST(REPLACE(Staff_ID, 'STF', '') AS INTEGER))
        FROM staff
        WHERE Staff_ID IS NOT NULL AND TRIM(Staff_ID) != ''
    """)
    result = cursor.fetchone()[0]
    conn.close()

    if result is None:
        return "STF1001"
    return f"STF{int(result) + 1}"


def phone_exists(phone, exclude_staff_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_staff_id:
        cursor.execute(
            "SELECT COUNT(*) FROM staff WHERE Phone = ? AND Staff_ID != ?",
            (phone, exclude_staff_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM staff WHERE Phone = ?",
            (phone,)
        )

    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def email_exists(email, exclude_staff_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_staff_id:
        cursor.execute(
            "SELECT COUNT(*) FROM staff WHERE Email = ? AND Staff_ID != ?",
            (email, exclude_staff_id)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM staff WHERE Email = ?",
            (email,)
        )

    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def add_staff(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO staff
        (
            Staff_ID, Employee_Name, Gender, Department, Designation,
            Qualification, Experience_Yrs, Joining_Date, Salary,
            Phone, Email, Status
        )
        VALUES (?,?,?,?,?, ?,?,?,?, ?,?,?)
    """, data)

    conn.commit()
    conn.close()


def get_staff_dict(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff WHERE Staff_ID = ?", (staff_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_staff(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE staff
        SET
            Employee_Name=?, Gender=?, Department=?, Designation=?,
            Qualification=?, Experience_Yrs=?, Salary=?,
            Phone=?, Email=?, Status=?
        WHERE Staff_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_staff(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE Staff_ID=?", (staff_id,))
    conn.commit()
    conn.close()