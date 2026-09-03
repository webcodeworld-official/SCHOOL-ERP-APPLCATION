from fpdf import FPDF
from database.connection import get_connection
from datetime import datetime


def get_fee_record_for_receipt(payment_id):
    """Fetches everything needed to print a receipt, joined with student info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.Payment_ID, f.Student_ID, s.First_Name, s.Last_Name, s.Class, s.Section,
               f.Month, f.Tuition_Fee, f.Transport_Fee, f.Library_Fee, f.Exam_Fee,
               f.Hostel_Fee, f.Books_Fee, f.Discount, f.Late_Fine, f.Total_Fee,
               f.Amount_Paid, f.Balance, f.Payment_Mode, f.Payment_Date, f.Payment_Status
        FROM fees f
        JOIN student s ON f.Student_ID = s.Student_ID
        WHERE f.Payment_ID = ?
    """, (payment_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    columns = [
        "Payment_ID", "Student_ID", "First_Name", "Last_Name", "Class", "Section",
        "Month", "Tuition_Fee", "Transport_Fee", "Library_Fee", "Exam_Fee",
        "Hostel_Fee", "Books_Fee", "Discount", "Late_Fine", "Total_Fee",
        "Amount_Paid", "Balance", "Payment_Mode", "Payment_Date", "Payment_Status",
    ]
    return dict(zip(columns, row))


def generate_receipt_pdf(payment_id, school_name="School ERP System"):
    """Returns PDF bytes for a fee payment receipt."""
    record = get_fee_record_for_receipt(payment_id)
    if record is None:
        return None

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, school_name, ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Fee Payment Receipt", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Receipt No: {record['Payment_ID']}", ln=True)
    pdf.cell(0, 7, f"Date: {record['Payment_Date'] or 'N/A'}", ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Student Details", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Name: {record['First_Name']} {record['Last_Name']}", ln=True)
    pdf.cell(0, 6, f"Student ID: {record['Student_ID']}", ln=True)
    pdf.cell(0, 6, f"Class: {record['Class']} - {record['Section']}", ln=True)
    pdf.cell(0, 6, f"Fee Month: {record['Month']}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Fee Breakdown", ln=True)
    pdf.set_font("Helvetica", "", 10)

    line_items = [
        ("Tuition Fee", record["Tuition_Fee"]),
        ("Transport Fee", record["Transport_Fee"]),
        ("Library Fee", record["Library_Fee"]),
        ("Exam Fee", record["Exam_Fee"]),
        ("Hostel Fee", record["Hostel_Fee"] or 0),
        ("Books Fee", record["Books_Fee"] or 0),
        ("Late Fine", record["Late_Fine"] or 0),
        ("Discount", -(record["Discount"] or 0)),
    ]
    for label, amount in line_items:
        if amount:
            pdf.cell(0, 6, f"{label}: Rs. {amount}", ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Total Fee: Rs. {record['Total_Fee']}", ln=True)
    pdf.cell(0, 7, f"Amount Paid: Rs. {record['Amount_Paid']}", ln=True)
    pdf.cell(0, 7, f"Balance Due: Rs. {record['Balance']}", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Payment Mode: {record['Payment_Mode'] or 'N/A'}", ln=True)
    pdf.cell(0, 6, f"Status: {record['Payment_Status']}", ln=True)

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")

    return bytes(pdf.output())
