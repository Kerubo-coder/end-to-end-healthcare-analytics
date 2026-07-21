import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

Path("outputs").mkdir(exist_ok=True)
df = pd.read_csv(r"C:\Users\nancy\Desktop\health_analytics\hospital_data.csv")
# Data inspection
print(df.head())
print("\nRows and Columns")
print(df.shape)
print("\nColumn Names")
print(df.columns.tolist())
print("\nData Types")
print(df.dtypes)

# Remove duplicate patient_ID columns (keep only the first one)
# Find all patient_ID columns
patient_id_cols = [col for col in df.columns if 'patient_id' in col.lower()]

if len(patient_id_cols) > 1:
    # Keep the first one, remove the rest
    cols_to_remove = patient_id_cols[1:]
    print(f"Found {len(patient_id_cols)} patient_ID column(s): {patient_id_cols}")
    print(f"Keeping: {patient_id_cols[0]}")
    print(f"Removing: {cols_to_remove}")
    df = df.drop(columns=cols_to_remove)
    print(f"New shape: {df.shape}")
elif len(patient_id_cols) == 1:
    print(f"Only one patient_ID column found: {patient_id_cols[0]}")
else:
    print("No patient_ID columns found.")

# Rename columns for clarity
df = df.rename(columns={
    "Total cost":"Total_Cost",
    "Treatment status":"Treatment_Status",
    "Treatment status.1":"Treatment_Status_1",
    "Date":"Date_of_Visit",
})
df = df.drop(columns=["Treatment_Status_1"], errors='ignore')  # Drop the duplicate column if it exists
print("\nColumn Names")
print(df.columns.to_list())

# Check for missing values
print(df.isnull().sum())

# missing values analysis
missing = (
    df.isnull()
      .sum()
      .to_frame("Missing")
)

missing["Percent"] = (
    missing["Missing"] / len(df) * 100
)

print(missing.sort_values("Percent", ascending=False))
# Visualize missing values
missing = df.isnull().sum()

missing = missing[missing > 0]

plt.figure(figsize=(10,5))

missing.plot(kind="bar")

plt.title("Missing Values by Column")

plt.ylabel("Count")

plt.tight_layout()

plt.savefig("outputs/missing_values.png")

plt.show()

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"Duplicate Rows: {duplicates}")

#convert date columns to date format (date only, no time)
date_columns = [
    "Date_of_Visit",
    "Admission_Date",
    "Discharge_Date"
]

for col in date_columns:
    df[col] = pd.to_datetime(df[col]).dt.date
print(df.dtypes)

# Fix invalid Admission and Discharge dates
# Convert date columns back to datetime for manipulation
df['Admission_Date'] = pd.to_datetime(df['Admission_Date'], errors='coerce')
df['Discharge_Date'] = pd.to_datetime(df['Discharge_Date'], errors='coerce')
df['Date_of_Visit'] = pd.to_datetime(df['Date_of_Visit'])

# Identify rows with invalid dates (missing or 1970)
invalid_admission = (df['Admission_Date'].isna()) | (df['Admission_Date'].dt.year == 1970)
invalid_discharge = (df['Discharge_Date'].isna()) | (df['Discharge_Date'].dt.year == 1970)

# For inpatient visits with invalid dates, generate dates based on Date_of_Visit
inpatient_mask = df['Visit_Type'].str.lower() == 'inpatient'

# Set invalid admission dates to same as visit date for inpatient
df.loc[inpatient_mask & invalid_admission, 'Admission_Date'] = df.loc[inpatient_mask & invalid_admission, 'Date_of_Visit']

# Set invalid discharge dates to 4 days after admission for inpatient
df.loc[inpatient_mask & invalid_discharge, 'Discharge_Date'] = df.loc[inpatient_mask & invalid_discharge, 'Admission_Date'] + pd.to_timedelta(4, unit='D')

# For outpatient visits, set both to NaT (null)
outpatient_mask = df['Visit_Type'].str.lower() == 'outpatient'
df.loc[outpatient_mask, 'Admission_Date'] = pd.NaT
df.loc[outpatient_mask, 'Discharge_Date'] = pd.NaT

print("Admission/Discharge dates generated based on Date_of_Visit:")
print(f"  - Inpatient: Admission = Visit Date, Discharge = Admission + 4 days")
print(f"  - Outpatient: Both set to NULL")

# Convert back to date format
df['Admission_Date'] = df['Admission_Date'].dt.date
df['Discharge_Date'] = df['Discharge_Date'].dt.date
df['Date_of_Visit'] = df['Date_of_Visit'].dt.date

# Rearrange columns: General Data -> Lab Data -> Pharmacy Data -> Admissions
# Desired column order
column_order = [

    # Patient Information
    "Patient_ID",
    "Age",
    "Gender",

    # Visit Information
    "Date_of_Visit",
    "Visit_Type",
    "Department",

        # Laboratory Results
    "Blood_Glucose",
    "Cholesterol",
    "Hemoglobin",
    "WBC_Count",
    "Platelet_Count",

    # Clinical Information
    "Diagnosis",

    # Medication
    "Medication",
    "Dosage_mg",
    # Admission Information
    "Admission_Date",
    "Discharge_Date",
    "Treatment_Status",

    # Financial
    "Total_Cost",
    # Doctor Name
    "Doctor"
]

# Keep only columns that actually exist
column_order = [col for col in column_order if col in df.columns]

# Add any remaining columns that were not specified
remaining_columns = [col for col in df.columns if col not in column_order]

# Rearrange the dataframe
df = df[column_order + remaining_columns]

# Display the new order
print(df.columns)


# Outlier detection using IQR method
numeric_columns = df.select_dtypes(include="number").columns

for col in numeric_columns:

    Q1 = df[col].quantile(.25)

    Q3 = df[col].quantile(.75)

    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR

    upper = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower) | (df[col] > upper)]

    print(f"{col}: {len(outliers)} outliers")

# categorical data analysis
categorical = [
    "Gender",
    "Department",
    "Diagnosis",
    "Visit_Type",
    "Medication",
    "Treatment_Status"
]

for col in categorical:

    print(df[col].value_counts())

# statistical summary of the dataset
summary = df.describe()

print(summary)
df.to_csv("outputs/statistical_summary.csv", index=False)

# Data quality report
import openpyxl
quality_report = pd.DataFrame({
    "Data_Type": df.dtypes.astype(str),
    "Missing_Values": df.isnull().sum(),
    "Unique_Values": df.nunique()
})

quality_report.to_excel(
    "outputs/data_quality_report.xlsx"
)

print(quality_report)

# Add Dr. prefix to Doctor column
def add_dr_prefix(name):
    if pd.isna(name):
        return name
    name = str(name).strip()
    if name == '' or name.lower().startswith('dr.'):
        return name
    return f'Dr. {name}'

df['Doctor'] = df['Doctor'].apply(add_dr_prefix)

# Display only the Doctor column after appending the prefix
print('\nDoctor column after prefixing:')
print(df[['Doctor']].head(20).to_string(index=False))


# Save the cleaned dataset to a new CSV file
df.to_csv("outputs/cleaned_hospital_data.csv", index=False)