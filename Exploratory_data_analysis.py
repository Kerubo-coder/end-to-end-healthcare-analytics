import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

plt.style.use("ggplot")
#Load the cleaned dataset
df = pd.read_csv("outputs/cleaned_hospital_data.csv")
Path("outputs/charts").mkdir(parents=True, exist_ok=True)

# Build executive KPIs for the hospital data

# Create KPI summary dataframe
kpi_data = {
    'Metric': [
        'Total Patients',
        'Total Departments',
        'Total Diagnoses',
        'Average Patient Age',
        'Average Treatment Cost',
        'Total Revenue'
    ],
    'Value': [
        df['Patient_ID'].nunique(),
        df['Department'].nunique(),
        df['Diagnosis'].nunique(),
        f"{df['Age'].mean():.1f} years",
        f"${df['Total_Cost'].mean():,.2f}",
        f"${df['Total_Cost'].sum():,.2f}"
    ]
}

kpi_df = pd.DataFrame(kpi_data)

# Export to CSV
kpi_df.to_csv('outputs/Hospital_KPI_Summary.csv', index=False)
print("✓ CSV file exported: outputs/Hospital_KPI_Summary.csv")

# AGE & SEX DISTRIBUTION ANALYSIS
print("\n" + "="*50)
print("AGE & SEX DISTRIBUTION ANALYSIS")
print("="*50)

# Create a figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Age & Sex Distribution Analysis', fontsize=16, fontweight='bold')

# 1. Age Distribution Histogram
axes[0].hist(df['Age'], bins=20, color='steelblue', edgecolor='black', alpha=0.7)
axes[0].set_title('Age Distribution', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Age (years)')
axes[0].set_ylabel('Frequency')
axes[0].grid(True, alpha=0.3)

# 2. Sex Distribution Bar Chart
sex_counts = df['Gender'].value_counts()
colors = ['#FF6B6B', '#4ECDC4']
axes[1].bar(sex_counts.index, sex_counts.values, color=colors, edgecolor='black', alpha=0.8)
axes[1].set_title('Gender Distribution', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Count')
axes[1].grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, v in enumerate(sex_counts.values):
    axes[1].text(i, v + 5, str(v), ha='center', fontweight='bold')

# 3. Age Distribution by Gender (Box Plot)
df.boxplot(column='Age', by='Gender', ax=axes[2])
axes[2].set_title('Age Distribution by Gender', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Gender')
axes[2].set_ylabel('Age (years)')
plt.suptitle('')  # Remove the automatic title from boxplot

plt.tight_layout()
plt.savefig('outputs/charts/Age_Sex_Distribution.png', dpi=300, bbox_inches='tight')
print("✓ Chart saved: outputs/charts/Age_Sex_Distribution.png")
plt.close()

# DEMOGRAPHIC INSIGHTS
# Age statistics
age_mean = df['Age'].mean()
age_median = df['Age'].median()
age_std = df['Age'].std()
age_min = df['Age'].min()
age_max = df['Age'].max()

# Gender breakdown
gender_dist = df['Gender'].value_counts()
for gender, count in gender_dist.items():
    percentage = (count / len(df)) * 100
    print(f"  {gender}: {count} ({percentage:.1f}%)")

# Age groups
age_groups = pd.cut(df['Age'], bins=[0, 18, 35, 50, 65, 100], 
                     labels=['0-18', '19-35', '36-50', '51-65', '65+'])
for group, count in age_groups.value_counts().sort_index().items():
    percentage = (count / len(df)) * 100
    print(f"  {group}: {count} ({percentage:.1f}%)")

# Gender-Age cross-tabulation
print(f"\nGender-Age Cross-tabulation:")
gender_age = pd.crosstab(df['Gender'], age_groups, margins=True)
print(gender_age)

# Calculate insights
youngest_group_pct = (len(df[df['Age'] < 35]) / len(df)) * 100
oldest_group_pct = (len(df[df['Age'] > 65]) / len(df)) * 100
majority_gender = gender_dist.idxmax()
majority_pct = (gender_dist.max() / len(df)) * 100

print(f"\n3. Overall Assessment:")
if age_mean < 40:
    age_assessment = "relatively young patient population"
elif age_mean < 55:
    age_assessment = "middle-aged patient population"
else:
    age_assessment = "aging patient population"
print(f"   - The hospital serves a {age_assessment}")
print(f"   - Treatment strategy should account for age-related healthcare needs")

# Save insights to text file
with open('outputs/Demographic_Insights.txt', 'w') as f:
    f.write("HOSPITAL DEMOGRAPHIC ANALYSIS REPORT\n")
    f.write("="*50 + "\n\n")
    f.write(f"Age Statistics:\n")
    f.write(f"  Mean Age: {age_mean:.1f} years\n")
    f.write(f"  Median Age: {age_median:.1f} years\n")
    f.write(f"  Std Dev: {age_std:.1f} years\n")
    f.write(f"  Age Range: {age_min} - {age_max} years\n\n")
    f.write(f"Gender Distribution:\n")
    for gender, count in gender_dist.items():
        percentage = (count / len(df)) * 100
        f.write(f"  {gender}: {count} ({percentage:.1f}%)\n")
    f.write("\n" + "="*50 + "\n")
    f.write("KEY INSIGHTS\n")
    f.write("="*50 + "\n")
    f.write(f"1. Patient population has mean age of {age_mean:.1f} years\n")
    f.write(f"2. {majority_gender} patients comprise {majority_pct:.1f}% of population\n")
    f.write(f"3. Hospital serves a {age_assessment}\n")

print("\n✓ Insights saved: outputs/Demographic_Insights.txt")

dept = df["Department"].value_counts()

plt.figure(figsize=(12,6))

ax = dept.plot(kind="bar", color='steelblue', edgecolor='black', alpha=0.8)
for bar in ax.patches:
    ax.annotate(
        f'{int(bar.get_height()):,}',
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        ha='center', va='bottom', fontsize=10,
        xytext=(0, 5), textcoords='offset points'
    )

ax.set_title("Patients by Department")
ax.set_ylabel("Patients")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()

plt.savefig("outputs/charts/department_analysis.png", dpi=300, bbox_inches='tight')

plt.show()


# Monthly patient trend analysis per department
if 'Date_of_Visit' in df.columns:
    df['Date_of_Visit'] = pd.to_datetime(df['Date_of_Visit'], errors='coerce')
    missing_dates = df['Date_of_Visit'].isna().sum()
    if missing_dates > 0:
        print(f'⚠️ Converted Date_of_Visit with {missing_dates} missing values after coercion.')
else:
    raise KeyError('Date_of_Visit column not found in dataframe')

monthly_dept = (
    df.dropna(subset=['Date_of_Visit'])
      .groupby([df['Date_of_Visit'].dt.to_period('M'), 'Department'])
      .size()
      .unstack(fill_value=0)
)
monthly_dept.index = monthly_dept.index.astype(str)

fig, ax = plt.subplots(figsize=(14, 7))
monthly_dept.plot(ax=ax, marker='o', linewidth=2)
ax.set_title('Monthly Patient Visits by Department', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Patient Visits')
ax.grid(True, alpha=0.3)
ax.legend(title='Department', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.savefig('outputs/charts/monthly_department_trends.png', dpi=300, bbox_inches='tight')
print('✓ Chart saved: outputs/charts/monthly_department_trends.png')
plt.close()

# Monthly department insights
department_totals = monthly_dept.sum().sort_values(ascending=False)
peak_month = monthly_dept.sum(axis=1).idxmax()
peak_department = department_totals.index[0]
peak_department_visits = department_totals.iloc[0]
most_growth_dept = monthly_dept.diff().sum().sort_values(ascending=False).index[0]

insight_lines = [
    'MONTHLY PATIENT TRENDS BY DEPARTMENT',
    '='*60,
    f'Peak month overall: {peak_month}',
    f'Most active department: {peak_department} ({peak_department_visits:,} total visits)',
    f'Department with strongest month-over-month increase: {most_growth_dept}',
    '',
    'Top 3 departments by total visits:'
]
for dept_name, total in department_totals.head(3).items():
    insight_lines.append(f'  - {dept_name}: {total:,} visits')

with open('outputs/Monthly_Department_Trends_Insights.txt', 'w') as f:
    f.write('\n'.join(insight_lines) + '\n')

print('✓ Insights saved: outputs/Monthly_Department_Trends_Insights.txt')

#Lab analysis
lab_columns = [
    "Blood_Glucose",
    "Cholesterol",
    "Hemoglobin",
    "WBC_Count",
    "Platelet_Count"
]

lab_stats = df[lab_columns].describe()
lab_summary = lab_stats.to_string()

lab_means = df[lab_columns].mean()
lab_std = lab_stats.loc['std']
highest_mean = lab_means.idxmax()
lowest_mean = lab_means.idxmin()
most_variable = lab_std.idxmax()

insight_lines = [
    'LAB TEST SUMMARY',
    '='*60,
    lab_summary,
    '',
    'INSIGHTS',
    '='*60,
    f'Highest average lab value: {highest_mean} ({lab_means[highest_mean]:.2f})',
    f'Lowest average lab value: {lowest_mean} ({lab_means[lowest_mean]:.2f})',
    f'Most variable lab test: {most_variable} (std={lab_std[most_variable]:.2f})',
    f'Total records analyzed: {int(lab_stats.loc["count", lab_columns[0]]) if "count" in lab_stats.index else len(df)}'
]

with open('outputs/Lab_Analysis_Summary.txt', 'w') as f:
    f.write('\n'.join(insight_lines) + '\n')

print('✓ Lab analysis summary saved: outputs/Lab_Analysis_Summary.txt')

# Correlation analysis for numeric columns
numeric = df.select_dtypes(include=np.number)

corr = numeric.corr()
corr_rounded = corr.round(2)

print(corr_rounded)

# Build correlation insights
corr_pairs = (
    corr
    .stack()
    .reset_index(name='corr')
    .rename(columns={'level_0': 'var1', 'level_1': 'var2'})
)
corr_pairs = corr_pairs[corr_pairs['var1'] != corr_pairs['var2']]

corr_pairs['abs_corr'] = corr_pairs['corr'].abs()

strong_pairs = corr_pairs.sort_values(['abs_corr', 'corr'], ascending=[False, False])
seen = set()
unique_pairs = []
for _, row in strong_pairs.iterrows():
    pair = tuple(sorted((row['var1'], row['var2'])))
    if pair in seen:
        continue
    seen.add(pair)
    unique_pairs.append(row)
    if len(unique_pairs) >= 5:
        break

strongest_positive = [row for row in unique_pairs if row['corr'] > 0][:5]
strongest_negative = [row for row in unique_pairs if row['corr'] < 0][:5]

insight_lines = [
    'CORRELATION MATRIX INSIGHTS',
    '='*60,
    'Correlation matrix (rounded):',
    corr_rounded.to_string(),
    '',
    'Top correlated variable pairs:',
]
for row in strongest_positive:
    insight_lines.append(f"  - {row['var1']} & {row['var2']}: {row['corr']:.2f} (positive)")
if not strongest_positive:
    insight_lines.append('  - No positive correlations found')

insight_lines.append('')
insight_lines.append('Top negatively correlated variable pairs:')
for row in strongest_negative:
    insight_lines.append(f"  - {row['var1']} & {row['var2']}: {row['corr']:.2f} (negative)")
if not strongest_negative:
    insight_lines.append('  - No negative correlations found')

insight_lines.append('')
insight_lines.append(f'Total numeric variables analyzed: {len(corr.columns)}')
insight_lines.append(f'Total unique variable pairs evaluated: {int(len(corr.columns) * (len(corr.columns) - 1) / 2)}')

with open('outputs/Correlation_Matrix_Insights.txt', 'w') as f:
    f.write('\n'.join(insight_lines) + '\n')

print('✓ Correlation insights saved: outputs/Correlation_Matrix_Insights.txt')

# Visualize the correlation matrix
plt.figure(figsize=(10,8))

plt.imshow(corr)

plt.colorbar()

plt.xticks(
    range(len(corr.columns)),
    corr.columns,
    rotation=90
)

plt.yticks(
    range(len(corr.columns)),
    corr.columns
)

plt.title("Correlation Matrix")

plt.tight_layout()

plt.savefig("outputs/charts/correlation_heatmap.png")

plt.show()

# Cross analysis
# Build cross-analysis tables and save them to a single text file

def resolve_column(df, candidates, name):
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(f"None of the {name} columns found: {candidates}")

department_col = resolve_column(df, ['Department'], 'department')
treatment_col = resolve_column(df, ['Treatment_Status', 'Treatment status', 'Treatment status.1'], 'treatment status')
doctor_col = resolve_column(df, ['Doctor'], 'doctor')
gender_col = resolve_column(df, ['Gender'], 'gender')
visit_col = resolve_column(df, ['Visit_Type', 'Visit Type', 'Visit_Type.1'], 'visit type')

cross_treatment_dept = pd.crosstab(df[department_col], df[treatment_col], margins=True)
cross_treatment_doctor = pd.crosstab(df[doctor_col], df[treatment_col], margins=True)
cross_department_gender = pd.crosstab(df[department_col], df[gender_col], margins=True)
cross_department_visit = pd.crosstab(df[department_col], df[visit_col], margins=True)

# Generate brief insights for cross-analysis
most_common_treatment = cross_treatment_dept.drop('All', axis=0, errors='ignore').sum().drop('All', errors='ignore').idxmax()
most_active_department = cross_treatment_dept.drop('All', axis=0, errors='ignore').sum(axis=1).idxmax()
most_active_doctor = cross_treatment_doctor.drop('All', axis=0, errors='ignore').sum(axis=1).idxmax()
most_gender_skewed_department = (cross_department_gender.drop('All', axis=0, errors='ignore').drop('All', axis=1, errors='ignore').apply(lambda x: abs(x / x.sum() - 0.5).max(), axis=1)).idxmax()
most_common_visit_department = cross_department_visit.drop('All', axis=0, errors='ignore').sum(axis=1).idxmax()

insight_lines = [
    'CROSS ANALYSIS SUMMARY INSIGHTS',
    '='*80,
    f'Most common treatment status overall: {most_common_treatment}',
    f'Department with highest patient volume: {most_active_department}',
    f'Doctor with highest treatment count: {most_active_doctor}',
    f'Department with the strongest gender skew: {most_gender_skewed_department}',
    f'Department with most visits by visit type: {most_common_visit_department}',
    ''
]

with open('outputs/Cross_Analysis_Summary.txt', 'w') as f:
    f.write('CROSS ANALYSIS REPORT\n')
    f.write('='*80 + '\n\n')
    f.write('\n'.join(insight_lines) + '\n')
    f.write('\n')
    f.write('1. Treatment status by department\n')
    f.write(cross_treatment_dept.to_string())
    f.write('\n\n')
    f.write('2. Treatment status by doctor\n')
    f.write(cross_treatment_doctor.to_string())
    f.write('\n\n')
    f.write('3. Department by gender\n')
    f.write(cross_department_gender.to_string())
    f.write('\n\n')
    f.write('4. Department by visit type\n')
    f.write(cross_department_visit.to_string())
    f.write('\n')

print('✓ Cross analysis summary saved: outputs/Cross_Analysis_Summary.txt')