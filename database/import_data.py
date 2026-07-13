import pandas as pd
from database.connection import get_connection

conn = get_connection()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

excel_file = BASE_DIR / "data" / "schools_erp.xlsx"

excel = pd.ExcelFile(excel_file)

for sheet in excel.sheet_names:
    print(f"Importing {sheet}")

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet
    )

    df.to_sql(
        sheet.lower(),
        conn,
        if_exists="replace",
        index=False
    )

conn.close()
print("Database created successfully")
