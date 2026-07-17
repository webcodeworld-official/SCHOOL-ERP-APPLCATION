import pandas as pd
df = pd.read_excel("school_erp_realistic_data.xlsx", sheet_name="ATTENDANCE")
print("Rows in Excel file:", len(df))
print("Date range in Excel:", df["Date"].min(), "to", df["Date"].max())