import pandas as pd

input_file = "data/school's erp.xlsx"
output_file = "data/cleaned_school_erp.xlsx"

excel = pd.ExcelFile(input_file)

cleaned = {}

for sheet in excel.sheet_names:

    df = pd.read_excel(input_file, sheet_name=sheet)

    # Remove extra spaces from column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Remove duplicate rows
    df = df.drop_duplicates()

    cleaned[sheet] = df

with pd.ExcelWriter(output_file) as writer:
    for sheet, df in cleaned.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

print("Cleaning completed.")