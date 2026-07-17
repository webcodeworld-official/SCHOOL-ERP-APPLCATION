from database.connection import get_connection
import pandas as pd

ACADEMIC_MONTHS = ["April", "May", "June", "July", "August", "September",
                    "October", "November", "December", "January", "February", "March"]


def get_all_fees():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM fees", conn)
    conn.close()
    return df


def get_next_payment_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Payment_ID) FROM fees")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def get_active_students():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT Student_ID, First_Name, Last_Name, Class, Section, Fee_Category
        FROM student WHERE Status = 'Active'
    """, conn)
    conn.close()
    return df


def get_student_transport_fee(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Transport_Fee FROM transportation WHERE Student_ID = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return int(row[0]) if row else 0


def fee_record_exists(student_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM fees WHERE Student_ID = ? AND Month = ?",
        (student_id, month)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def add_fee_record(payment_id, student_id, month, tuition_fee, transport_fee, library_fee, exam_fee, discount):
    """Creates a new fee due record. Amount_Paid=0, Balance=Total_Fee, Status='Pending' at creation."""
    total_fee = tuition_fee + transport_fee + library_fee + exam_fee - discount
    balance = total_fee

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO fees
        (Payment_ID, Student_ID, Payment_Date, Month, Tuition_Fee, Transport_Fee,
         Library_Fee, Exam_Fee, Discount, Total_Fee, Amount_Paid, Balance,
         Payment_Mode, Payment_Status)
        VALUES (?,?,NULL,?,?,?,?,?,?,?,0,?,NULL,'Pending')
    """, (payment_id, student_id, month, tuition_fee, transport_fee, library_fee,
          exam_fee, discount, total_fee, balance))

    conn.commit()
    conn.close()


def get_fee_dict(payment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fees WHERE Payment_ID = ?", (payment_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def record_payment(payment_id, amount, payment_mode, payment_date):
    """Applies a payment installment. Recomputes Amount_Paid, Balance, and Status."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Total_Fee, Amount_Paid FROM fees WHERE Payment_ID = ?", (payment_id,))
    total_fee, current_paid = cursor.fetchone()
    current_paid = current_paid or 0

    new_paid = current_paid + amount
    new_balance = max(total_fee - new_paid, 0)
    status = "Paid" if new_balance == 0 else "Partial"

    cursor.execute("""
        UPDATE fees
        SET Amount_Paid = ?, Balance = ?, Payment_Status = ?, Payment_Date = ?, Payment_Mode = ?
        WHERE Payment_ID = ?
    """, (new_paid, new_balance, status, payment_date, payment_mode, payment_id))

    conn.commit()
    conn.close()

    return new_paid, new_balance, status


def update_fee_record(payment_id, tuition_fee, transport_fee, library_fee, exam_fee, discount):
    """Edits the fee components (not the payment itself) and recomputes Total_Fee/Balance/Status
    against whatever Amount_Paid already exists on the record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Amount_Paid FROM fees WHERE Payment_ID = ?", (payment_id,))
    amount_paid = cursor.fetchone()[0] or 0

    total_fee = tuition_fee + transport_fee + library_fee + exam_fee - discount
    balance = max(total_fee - amount_paid, 0)
    status = "Paid" if balance == 0 else ("Partial" if amount_paid > 0 else "Pending")

    cursor.execute("""
        UPDATE fees
        SET Tuition_Fee=?, Transport_Fee=?, Library_Fee=?, Exam_Fee=?,
            Discount=?, Total_Fee=?, Balance=?, Payment_Status=?
        WHERE Payment_ID=?
    """, (tuition_fee, transport_fee, library_fee, exam_fee, discount, total_fee, balance, status, payment_id))

    conn.commit()
    conn.close()


def delete_fee_record(payment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fees WHERE Payment_ID=?", (int(payment_id),))
    conn.commit()
    conn.close()
