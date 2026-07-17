from database.connection import get_connection
import pandas as pd
from datetime import date

FINE_PER_DAY_LATE = 5  # ₹5/day overdue, matches how the sample data was generated


def get_all_library_records():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM library", conn)
    conn.close()
    return df


def get_next_transaction_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(Transaction_ID AS INTEGER)) FROM library")
    result = cursor.fetchone()[0]
    conn.close()

    if result is None:
        return 1
    return int(result) + 1


def issue_book(data):
    """Issue a new book. Return_Date and Fine are always NULL at issue time."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO library
        (Transaction_ID, Student_ID, Book_ID, Book_Name, Issue_Date, Due_Date, Return_Date, Fine)
        VALUES (?,?,?,?,?,?,NULL,NULL)
    """, data)

    conn.commit()
    conn.close()


def return_book(transaction_id, return_date):
    """Marks a book as returned, auto-calculating fine based on days late."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Due_Date FROM library WHERE Transaction_ID = ?", (transaction_id,))
    due_date_str = cursor.fetchone()[0]
    due_date = date.fromisoformat(due_date_str)

    days_late = max((return_date - due_date).days, 0)
    fine = days_late * FINE_PER_DAY_LATE

    cursor.execute("""
        UPDATE library
        SET Return_Date = ?, Fine = ?
        WHERE Transaction_ID = ?
    """, (return_date.isoformat(), fine, transaction_id))

    conn.commit()
    conn.close()

    return fine


def get_library_record_dict(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM library WHERE Transaction_ID = ?", (transaction_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    if row is None:
        return None
    return dict(zip(columns, row))


def update_library_record(data):
    """Edits the core details of a transaction. Does NOT touch Return_Date/Fine —
    use return_book() for that, to keep the fine calculation consistent."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE library
        SET Student_ID=?, Book_ID=?, Book_Name=?, Issue_Date=?, Due_Date=?
        WHERE Transaction_ID=?
    """, data)

    conn.commit()
    conn.close()


def delete_library_record(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM library WHERE Transaction_ID=?", (int(transaction_id),))
    conn.commit()
    conn.close()
