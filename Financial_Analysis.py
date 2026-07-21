import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

plt.style.use("ggplot")

#Load the cleaned dataset
df = pd.read_csv("outputs/cleaned_hospital_data.csv")
Path("outputs/financial_charts").mkdir(parents=True, exist_ok=True)

# Financial KPIs for the hospital data
financial_kpis = {
    'Metric': [
        'Total Revenue',
        'Average Treatment Cost',
        'Median Treatment Cost',
        'Highest Treatment Cost',
        'Lowest Treatment Cost',
        'Average Inpatient Cost',
        'Average Outpatient Cost'
    ],
    'Value': []
}

total_revenue = df['Total_Cost'].sum()
avg_cost = df['Total_Cost'].mean()
median_cost = df['Total_Cost'].median()
max_cost = df['Total_Cost'].max()
min_cost = df['Total_Cost'].min()

inpatient_mask = df['Visit_Type'].str.lower() == 'inpatient'
outpatient_mask = df['Visit_Type'].str.lower() == 'outpatient'

avg_inpatient_cost = df.loc[inpatient_mask, 'Total_Cost'].mean()
avg_outpatient_cost = df.loc[outpatient_mask, 'Total_Cost'].mean()

financial_kpis['Value'] = [
    f'${total_revenue:,.2f}',
    f'${avg_cost:,.2f}',
    f'${median_cost:,.2f}',
    f'${max_cost:,.2f}',
    f'${min_cost:,.2f}',
    f'${avg_inpatient_cost:,.2f}' if not np.isnan(avg_inpatient_cost) else 'N/A',
    f'${avg_outpatient_cost:,.2f}' if not np.isnan(avg_outpatient_cost) else 'N/A'
]

kpi_df = pd.DataFrame(financial_kpis)
summary_text = kpi_df.to_string(index=False)

with open('outputs/Financial_KPI_Summary.txt', 'w') as f:
    f.write('FINANCIAL KPI SUMMARY\n')
    f.write('='*60 + '\n')
    f.write(summary_text + '\n\n')

print('✓ Financial KPI summary saved: outputs/Financial_KPI_Summary.txt')

# Visualize the revenue by department
department_cost = df.groupby('Department')['Total_Cost'].sum().sort_values(ascending=False)
plt.figure(figsize=(12,6))

ax = department_cost.plot(kind="bar", color='green', edgecolor='black', alpha=0.85)
for bar in ax.patches:
    height = bar.get_height()
    ax.annotate(
        f'${height:,.0f}',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords='offset points',
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold'
    )

plt.title("Revenue by Department")

plt.ylabel("Revenue")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig("outputs/financial_charts/revenue_department.png", dpi=300, bbox_inches='tight')

plt.show()

diagnosis_cost = (
    df.groupby("Diagnosis")["Total_Cost"]
      .sum()
      .sort_values(ascending=False)
)

diagnosis_cost.head(10)

plt.figure(figsize=(12,6))
ax = diagnosis_cost.head(10).plot(kind="bar", color='orange', edgecolor='black', alpha=0.85)
for bar in ax.patches:
    height = bar.get_height()
    ax.annotate(
        f'${height:,.0f}',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords='offset points',
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold'
    )

plt.title("Top 10 Diagnoses by Revenue")

plt.tight_layout()

plt.savefig("outputs/financial_charts/diagnosis_revenue.png", dpi=300, bbox_inches='tight')

plt.show()

# Revenue trend per doctor
if 'Date_of_Visit' in df.columns:
    df['Date_of_Visit'] = pd.to_datetime(df['Date_of_Visit'], errors='coerce')
    doctor_revenue_trend = (
        df.dropna(subset=['Date_of_Visit'])
          .groupby([df['Date_of_Visit'].dt.to_period('M'), 'Doctor'])['Total_Cost']
          .sum()
          .unstack(fill_value=0)
    )
    doctor_revenue_trend.index = doctor_revenue_trend.index.astype(str)

    fig, ax = plt.subplots(figsize=(14, 8))
    doctor_revenue_trend.plot(ax=ax, marker='o', linewidth=2)
    ax.set_title('Monthly Revenue Trend by Doctor', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue')
    ax.grid(True, alpha=0.3)
    ax.legend(title='Doctor', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('outputs/financial_charts/revenue_trend_doctor.png', dpi=300, bbox_inches='tight')
    plt.show()
else:
    print('⚠️ Date_of_Visit column missing; cannot generate revenue trend per doctor.')

# Age group analysis for revenue
bins = [0,18,35,50,65,120]

labels = [
    "Child",
    "Young Adult",
    "Adult",
    "Middle Age",
    "Senior"
]

df["Age_Group"] = pd.cut(
    df["Age"],
    bins=bins,
    labels=labels
)

age_cost = (
    df.groupby("Age_Group")["Total_Cost"]
      .mean()
)

age_cost_table = age_cost.reset_index()
age_cost_table.columns = ["Age Group", "Average Treatment Cost"]
age_cost_table["Average Treatment Cost"] = age_cost_table["Average Treatment Cost"].apply(lambda x: f'${x:,.2f}')

summary_text = age_cost_table.to_string(index=False)

age_insights = [
    "AVERAGE TREATMENT COST BY AGE GROUP",
    "="*60,
    summary_text,
    "",
    "INSIGHTS",
    "="*60,
]
if not age_cost.empty:
    age_insights.extend([
        f'Highest average cost age group: {age_cost.idxmax()} (${age_cost.max():,.2f})',
        f'Lowest average cost age group: {age_cost.idxmin()} (${age_cost.min():,.2f})',
        f'Overall average age-group cost: ${age_cost.mean():,.2f}',
    ])
else:
    age_insights.append('No age-group cost data available.')

with open('outputs/Financial_Age_Group_Cost_Summary.txt', 'w') as f:
    f.write('\n'.join(age_insights) + '\n')

print('✓ Age group cost summary saved: outputs/Financial_Age_Group_Cost_Summary.txt')

# Top 20 customer revenue contributors
top_patients = (
    df.sort_values(
        by="Total_Cost",
        ascending=False
    )
    [["Patient_ID",
      "Department",
      "Diagnosis",
      "Total_Cost"]]
    .head(20)
)

top_patients.to_csv(
    "outputs/top_20_high_cost_patients.csv",
    index=False
)