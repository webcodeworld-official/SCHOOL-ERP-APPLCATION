import streamlit as st
from database.fee_structure_queries import (
    get_all_fee_types, get_fee_structure, upsert_structure_amount,
    get_students_for_generation, generate_fee_schedule
)
from database.fees_queries import ACADEMIC_MONTHS
from database.student_queries import get_current_academic_year
from database.branch_queries import get_branch_name
from utils import load_custom_css
from datetime import date, timedelta
import pandas as pd

load_custom_css()

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

active_branch_id = st.session_state.get("active_branch_id")

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">ERP Management</div>
    <div class="erp-title">⚙️ Fee Structure Management</div>
    <div class="erp-subtitle">Define fee templates per Class, then generate fee schedules in bulk.</div>
</div>
""", unsafe_allow_html=True)

st.caption(f"🏢 Viewing: **{get_branch_name(active_branch_id)}**")

tab_structure, tab_generate, tab_fines, tab_receipt = st.tabs([
    "⚙️ Define Fee Structure", "📋 Generate Fee Schedule", "⏰ Late Fines", "🧾 Generate Receipt"
])

with tab_structure:
    from database.fee_structure_queries import get_defined_structure_summary

    st.caption("📋 Classes with a fee structure already defined for this year:")

    summary = get_defined_structure_summary(get_current_academic_year(), active_branch_id)

    all_classes = [str(i) for i in range(1, 13)]
    defined_combos = set(
        zip(summary["Class"], summary["Stream"].fillna(""))
    ) if not summary.empty else set()

    # Build a lookup: (Class, Stream) -> Total_Base_Fee, for quick access
    amount_lookup = {}
    if not summary.empty:
        for _, row in summary.iterrows():
            key = (row["Class"], row["Stream"] or "")
            amount_lookup[key] = int(row["Total_Base_Fee"])

    status_rows = []
    for cls in all_classes:
        if cls in ("11", "12"):
            for stream in ["Science", "Commerce", "Arts"]:
                key = (cls, stream)
                if key in amount_lookup:
                    status_rows.append({"Class": cls, "Stream": stream, "Total Fee (per month)": f"₹{amount_lookup[key]:,}", "Status": "✅ Set"})
                else:
                    status_rows.append({"Class": cls, "Stream": stream, "Total Fee (per month)": "—", "Status": "❌ Not defined"})
        else:
            key = (cls, "")
            if key in amount_lookup:
                status_rows.append({"Class": cls, "Stream": "—", "Total Fee (per month)": f"₹{amount_lookup[key]:,}", "Status": "✅ Set"})
            else:
                status_rows.append({"Class": cls, "Stream": "—", "Total Fee (per month)": "—", "Status": "❌ Not defined"})

    status_df = pd.DataFrame(status_rows)
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    st.divider()
    st.caption("Set or update the structure for a specific Class below:")

    st.caption("Set the standard fee amount for each fee type, per Class (and Stream, for 11-12).")

    col1, col2, col3 = st.columns(3)
    with col1:
        struct_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="struct_class")
    with col2:
        struct_stream = None
        if struct_class in ("11", "12"):
            struct_stream = st.selectbox("Stream", ["Science", "Commerce", "Arts"], key="struct_stream")
        else:
            st.text_input("Stream", value="N/A (not applicable)", disabled=True, key="struct_stream_na")
    with col3:
        struct_year = st.text_input("Academic Year", value=get_current_academic_year(), key="struct_year")

    fee_types = get_all_fee_types()
    existing_structure = get_fee_structure(struct_class, struct_stream, struct_year, active_branch_id)
    existing_amounts = dict(zip(existing_structure["Fee_Type_Name"], existing_structure["Amount"]))

    st.divider()
    st.caption(f"Fee amounts for Class {struct_class}" + (f" ({struct_stream})" if struct_stream else "") + f" — {struct_year}")

    entered_amounts = {}
    cols = st.columns(2)
    for i, (_, ft) in enumerate(fee_types.iterrows()):
        col = cols[i % 2]
        with col:
            label = f"{ft['Fee_Type_Name']}" + (" (optional)" if ft["Is_Optional"] == "Y" else "")
            amount = st.number_input(
                label, min_value=0,
                value=int(existing_amounts.get(ft["Fee_Type_Name"], 0)),
                key=f"amt_{ft['Fee_Type_ID']}"
            )
            entered_amounts[ft["Fee_Type_ID"]] = amount

    if st.button("💾 Save Fee Structure", use_container_width=True):
        if active_branch_id is None:
            st.error("Select a specific branch (not 'All Branches') before saving a structure.")
        else:
            for fee_type_id, amount in entered_amounts.items():
                upsert_structure_amount(struct_class, struct_stream, struct_year, fee_type_id, amount, active_branch_id)
            st.success(f"Fee structure saved for Class {struct_class}" + (f" ({struct_stream})" if struct_stream else "") + ".")

with tab_generate:
    st.caption("Bulk-generate fee due records for every active student in a Class-Section, using the saved structure.")

    col1, col2, col3 = st.columns(3)
    with col1:
        gen_class = st.selectbox("Class", [str(i) for i in range(1, 13)], key="gen_class")
    with col2:
        gen_section = st.selectbox("Section", ["A", "B", "C"], key="gen_section")
    with col3:
        gen_stream = None
        if gen_class in ("11", "12"):
            gen_stream = st.selectbox("Stream", ["Science", "Commerce", "Arts"], key="gen_stream")

    col4, col5, col6 = st.columns(3)
    with col4:
        gen_month = st.selectbox("Month", ACADEMIC_MONTHS, key="gen_month")
    with col5:
        gen_year = st.text_input("Academic Year", value=get_current_academic_year(), key="gen_year")
    with col6:
        gen_due_date = st.date_input("Due Date", value=date.today() + timedelta(days=10), key="gen_due_date")

    preview_students = get_students_for_generation(gen_class, gen_section, gen_stream, active_branch_id)
    st.caption(f"{len(preview_students)} active student(s) match this Class-Section" + (f"-{gen_stream}" if gen_stream else ""))

    if not preview_students.empty:
        st.dataframe(
            preview_students[["Student_ID", "First_Name", "Last_Name"]],
            use_container_width=True, hide_index=True
        )

    if st.button("🚀 Generate Fee Schedule", use_container_width=True):
        if active_branch_id is None:
            st.error("Select a specific branch (not 'All Branches') before generating.")
        else:
            created, skipped, error = generate_fee_schedule(
                gen_class, gen_section, gen_stream, gen_month, gen_year,
                gen_due_date.isoformat(), active_branch_id
            )
            if error:
                st.error(error)
            else:
                st.success(f"✅ Generated {created} fee record(s). Skipped {skipped} (already had a record for {gen_month}).")

with tab_fines:
    from database.fees_queries import get_overdue_fees, recalculate_late_fines

    st.caption("Preview and apply late fines for overdue, unpaid fee records.")

    fine_rate = st.number_input("Fine per day late (₹)", min_value=0, value=10, key="fine_rate")

    overdue = get_overdue_fees(branch_id=active_branch_id)
    st.caption(f"{len(overdue)} overdue record(s) found")

    if not overdue.empty:
        st.dataframe(
            overdue[["Payment_ID", "First_Name", "Last_Name", "Month", "Balance", "Due_Date", "Late_Fine"]],
            use_container_width=True, hide_index=True
        )

        if st.button("⏰ Apply Late Fines", use_container_width=True):
            if active_branch_id is None:
                st.error("Select a specific branch (not 'All Branches') before applying fines.")
            else:
                updated = recalculate_late_fines(branch_id=active_branch_id, fine_per_day=fine_rate)
                st.success(f"Late fines applied to {updated} overdue record(s).")

with tab_receipt:
    from database.receipt_generator import generate_receipt_pdf, get_fee_record_for_receipt

    st.caption("Enter a Payment ID to generate a printable receipt.")

    receipt_payment_id = st.text_input("Payment ID", key="receipt_payment_id")

    if receipt_payment_id:
        record = get_fee_record_for_receipt(receipt_payment_id)
        if record is None:
            st.error("No fee record found with this Payment ID.")
        else:
            st.info(
                f"**{record['First_Name']} {record['Last_Name']}** — "
                f"Class {record['Class']}-{record['Section']} — {record['Month']} — "
                f"₹{record['Amount_Paid']} paid of ₹{record['Total_Fee']}"
            )

            if st.button("🧾 Generate Receipt PDF", use_container_width=True):
                pdf_bytes = generate_receipt_pdf(receipt_payment_id)
                st.session_state["receipt_pdf"] = pdf_bytes
                st.session_state["receipt_filename"] = f"receipt_{receipt_payment_id}.pdf"

    if "receipt_pdf" in st.session_state:
        st.download_button(
            "⬇️ Download Receipt",
            data=st.session_state["receipt_pdf"],
            file_name=st.session_state["receipt_filename"],
            mime="application/pdf"
        )