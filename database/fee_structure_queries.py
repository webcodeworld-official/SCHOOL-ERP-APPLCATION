from database.connection import get_connection
import pandas as pd
from database.admission_queries import get_admission_discount_percentage
from database.fees_queries import get_student_transport_fee
from database.student_queries import get_current_academic_year

def get_all_fee_types():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM fee_types ORDER BY Fee_Type_ID", conn)
    conn.close()
    return df


def get_fee_structure(class_, stream, academic_year, branch_id):
    """Returns the defined structure rows for a Class/Stream/Year/Branch, joined with fee type names."""
    conn = get_connection()
    query = """
        SELECT fs.Structure_ID, fs.Fee_Type_ID, ft.Fee_Type_Name, ft.Is_Optional, fs.Amount
        FROM fee_structure fs
        JOIN fee_types ft ON fs.Fee_Type_ID = ft.Fee_Type_ID
        WHERE fs.Class = ? AND fs.Academic_Year = ?
    """
    params = [class_, academic_year]

    if stream:
        query += " AND fs.Stream = ?"
        params.append(stream)
    else:
        query += " AND fs.Stream IS NULL"

    if branch_id is not None:
        query += " AND fs.Branch_ID = ?"
        params.append(branch_id)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


def upsert_structure_amount(class_, stream, academic_year, fee_type_id, amount, branch_id):
    """Sets (or updates) the amount for one fee type in a Class/Stream template."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Structure_ID FROM fee_structure
        WHERE Class = ? AND Academic_Year = ? AND Fee_Type_ID = ?
        AND (Stream = ? OR (Stream IS NULL AND ? IS NULL))
        AND (Branch_ID = ? OR (Branch_ID IS NULL AND ? IS NULL))
    """, (class_, academic_year, fee_type_id, stream, stream, branch_id, branch_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE fee_structure SET Amount = ? WHERE Structure_ID = ?", (amount, existing[0]))
    else:
        cursor.execute("SELECT MAX(Structure_ID) FROM fee_structure")
        max_id = cursor.fetchone()[0]
        new_id = 1 if max_id is None else int(max_id) + 1
        cursor.execute("""
            INSERT INTO fee_structure (Structure_ID, Class, Stream, Academic_Year, Fee_Type_ID, Amount, Branch_ID)
            VALUES (?,?,?,?,?,?,?)
        """, (new_id, class_, stream, academic_year, fee_type_id, amount, branch_id))

    conn.commit()
    conn.close()


def get_students_for_generation(class_, section, stream, branch_id):
    conn = get_connection()
    query = """
        SELECT Student_ID, First_Name, Last_Name, Transport_ID
        FROM student
        WHERE Class = ? AND Section = ? AND Status = 'Active'
    """
    params = [class_, section]

    if stream:
        query += " AND Stream = ?"
        params.append(stream)

    if branch_id is not None:
        query += " AND Branch_ID = ?"
        params.append(branch_id)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


def fee_record_exists_for_month(student_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fees WHERE Student_ID = ? AND Month = ?", (student_id, month))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def get_next_payment_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Payment_ID) FROM fees")
    result = cursor.fetchone()[0]
    conn.close()
    return 1 if result is None else int(result) + 1


def generate_fee_schedule(class_, section, stream, month, academic_year, due_date, branch_id):
    """
    Bulk-generates fee records for every active student in a Class-Section,
    using the defined Fee Structure, auto-applying their Admission discount
    and their actual Transport fee (if assigned). Skips students who already
    have a record for that month.

    Returns (created_count, skipped_count).
    """
    structure = get_fee_structure(class_, stream, academic_year, branch_id)
    if structure.empty:
        return 0, 0, "No fee structure defined for this Class/Stream/Year. Set it up first."

    structure_by_type = dict(zip(structure["Fee_Type_Name"], structure["Amount"]))

    students = get_students_for_generation(class_, section, stream, branch_id)
    if students.empty:
        return 0, 0, "No active students found for this Class-Section."

    conn = get_connection()
    cursor = conn.cursor()

    created = 0
    skipped = 0

    for _, s in students.iterrows():
        student_id = int(s["Student_ID"])

        if fee_record_exists_for_month(student_id, month):
            skipped += 1
            continue

        tuition = structure_by_type.get("Tuition", 0)
        library = structure_by_type.get("Library", 0)
        exam = structure_by_type.get("Exam", 0)
        hostel = structure_by_type.get("Hostel", 0)
        books = structure_by_type.get("Books", 0)

        # Transport: prefer the student's ACTUAL assigned fee from Transport Management
        # over the flat structure amount, since real distance-based fees vary per student.
        transport = get_student_transport_fee(student_id) if s["Transport_ID"] else 0
        if transport == 0:
            transport = structure_by_type.get("Transport", 0)

        discount_pct = get_admission_discount_percentage(student_id)
        base_total = tuition + transport + library + exam + hostel + books
        discount = int(base_total * discount_pct / 100) if discount_pct else 0

        total_fee = base_total - discount
        payment_id = get_next_payment_id()

        cursor.execute("""
            INSERT INTO fees
            (Payment_ID, Student_ID, Payment_Date, Month, Tuition_Fee, Transport_Fee,
             Library_Fee, Exam_Fee, Discount, Total_Fee, Amount_Paid, Balance,
             Payment_Mode, Payment_Status, Hostel_Fee, Books_Fee, Due_Date, Late_Fine)
            VALUES (?,?,NULL,?,?,?,?,?,?,?,0,?,NULL,'Pending',?,?,?,0)
        """, (
            payment_id, student_id, month, tuition, transport, library, exam,
            discount, total_fee, total_fee, hostel, books, due_date
        ))

        created += 1

    conn.commit()
    conn.close()

    return created, skipped, None

def auto_generate_yearly_fee_schedule(student_id, class_, stream, academic_year, branch_id, discount_pct, has_transport):
    """
    Called right after a new admission is processed. Generates the FULL
    year's (April-March) fee schedule for ONE student at once, using the
    pre-defined Fee Structure for their class and their calculated discount.
    """
    structure = get_fee_structure(class_, stream, academic_year, branch_id)
    if structure.empty:
        return 0, "No fee structure defined yet for this Class/Stream/Year. Define it in Fee Structure Management first, then re-run generation."

    structure_by_type = dict(zip(structure["Fee_Type_Name"], structure["Amount"]))
    tuition = structure_by_type.get("Tuition", 0)
    library = structure_by_type.get("Library", 0)
    exam = structure_by_type.get("Exam", 0)
    hostel = structure_by_type.get("Hostel", 0)
    books = structure_by_type.get("Books", 0)

    transport = get_student_transport_fee(student_id) if has_transport else 0
    if transport == 0:
        transport = structure_by_type.get("Transport", 0)

    base_total = tuition + transport + library + exam + hostel + books
    discount = int(base_total * discount_pct / 100) if discount_pct else 0
    total_fee = base_total - discount

    months = ["April", "May", "June", "July", "August", "September",
              "October", "November", "December", "January", "February", "March"]

    conn = get_connection()
    cursor = conn.cursor()
    created = 0

    for month in months:
        cursor.execute("SELECT COUNT(*) FROM fees WHERE Student_ID = ? AND Month = ?", (student_id, month))
        if cursor.fetchone()[0] > 0:
            continue

        cursor.execute("SELECT MAX(Payment_ID) FROM fees")
        max_id = cursor.fetchone()[0]
        payment_id = 1 if max_id is None else int(max_id) + 1

        cursor.execute("""
            INSERT INTO fees
            (Payment_ID, Student_ID, Payment_Date, Month, Tuition_Fee, Transport_Fee,
             Library_Fee, Exam_Fee, Discount, Total_Fee, Amount_Paid, Balance,
             Payment_Mode, Payment_Status, Hostel_Fee, Books_Fee, Due_Date, Late_Fine)
            VALUES (?,?,NULL,?,?,?,?,?,?,?,0,?,NULL,'Pending',?,?,NULL,0)
        """, (payment_id, student_id, month, tuition, transport, library, exam,
              discount, total_fee, total_fee, hostel, books))
        created += 1

    conn.commit()
    conn.close()
    return created, None

def get_defined_structure_summary(academic_year, branch_id):
    """Returns one row per Class(+Stream) that has ANY structure defined,
    showing the total of all fee types combined — a quick overview of coverage."""
    conn = get_connection()
    query = """
        SELECT fs.Class, fs.Stream, SUM(fs.Amount) AS Total_Base_Fee, COUNT(*) AS Fee_Types_Set
        FROM fee_structure fs
        WHERE fs.Academic_Year = ?
    """
    params = [academic_year]

    if branch_id is not None:
        query += " AND fs.Branch_ID = ?"
        params.append(branch_id)

    query += " GROUP BY fs.Class, fs.Stream ORDER BY CAST(fs.Class AS INTEGER), fs.Stream"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df