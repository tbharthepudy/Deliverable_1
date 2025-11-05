import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt

load_dotenv()

username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASS")
database = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")

# SQLAlchemy connection string
engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

df = pd.read_sql("SELECT * FROM data_table", engine)

print(df.info())

# Make column names consistent 
df.columns = df.columns.str.lower()

# Convert data types
numeric_cols = ['data_value', 'low_confidence_limit', 'high_confidence_limit', 'totalpopulation', 'totalpop18plus', 'locationid']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert year to integer 
if 'year' in df.columns:
    df['year'] = pd.to_datetime(df['year'], errors='coerce').dt.year

# Remove unwanted columns (system columns from API)
drop_cols = ['datasource', 'categoryid', 'measureid', ':@computed_region_hjsp_umg2', ':created_at', ':updated_at', 'data_value_footnote_symbol', 'data_value_footnote',
             ':id', ':version', 'stateabbr', ':@computed_region_skr5_azej' ]
df.drop(columns=drop_cols, inplace = True)

# Handle missing data
df = df.dropna(subset=['locationname', 'longitude', 'latitude'])

# Renaming column names
df.rename(columns={
    'statedesc': 'state',
    'locationname': 'county',
    'data_value': 'prevalence_rate',
    'short_question_text': 'health_issue'
}, inplace=True)

# Calculate people affected
df['people_with_measure'] = (df['prevalence_rate'] / 100) * df['totalpopulation']

# State-wise & Year-wise Aggregations & Trend changes over Time
state_summary = (
    df.groupby(['state', 'health_issue','year'])
      .agg(
           total_affected=('people_with_measure', 'sum'),
           total_pop=('totalpopulation', 'sum'))
      .reset_index()
)

year_summary = (
    df.groupby(['year', 'health_issue'])
      .agg(avg_value=('prevalence_rate', 'mean'))
      .reset_index()
)



location_summary = (
    df.groupby(['county', 'health_issue'])
      .agg(
          total_population=('totalpopulation', 'sum'),
          total_affected=('people_with_measure', 'sum')
      )
      .reset_index()
)

# print("Cleaned Data Overview:")
# print(df.info())
# print("Missing values per column:")
# print(df.isna().sum())

# VISUALIZATIONS

# 1. Which states have the highest obesity prevalence?

obesity = df[df['health_issue'].str.contains('obesity', case=False)]
obesity_state = obesity.groupby('state')['prevalence_rate'].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(10,6))
ax = sns.barplot(x=obesity_state.values, y=obesity_state.index, palette="Reds_r")
plt.title("Top 10 States with Highest Obesity Prevalence")
plt.xlabel("Average Obesity (%)")
plt.ylabel("State")
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', label_type='center', padding=3)
plt.show()


# 2. Which states have the lowest arthritis prevalence?

arthritis = df[df['health_issue'].str.contains('arthritis', case=False)]
arthritis_state = arthritis.groupby('state')['prevalence_rate'].mean().sort_values(ascending=True).head(15)

plt.figure(figsize=(10,6))
ax = sns.barplot(x=arthritis_state.index, y=arthritis_state.values, palette="Blues_r")
plt.title("Top 15 States with Lowest Arthritis Prevalence")
plt.xlabel("Average Arthritis (%)")
plt.xticks(rotation=90)
plt.ylabel("State")
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', label_type='edge', padding=3)
plt.show()

# 3. Correlation between Asthma, Smoking, and Obesity (Heatmap)

corr_df = df[df['health_issue'].str.contains('obesity|smoking|asthma', case=False)]
corr_pivot = corr_df.pivot_table(
    index='state',
    columns='health_issue',
    values='prevalence_rate',
    aggfunc='mean'
).dropna(axis=1, how='all')

plt.figure(figsize=(10,6))
sns.heatmap(corr_pivot.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap: Asthma, Smoking, Obesity")
plt.show()

# 4. Geographic Distribution of Risk Behaviors

risk_behaviors = df[df['category'].str.contains('Risk Behavior', case=False, na=False)]

plt.figure(figsize=(10,6))
sns.scatterplot(data=risk_behaviors, x='longitude', y='latitude', hue='prevalence_rate', size='prevalence_rate', palette='viridis')
plt.title("Geographic Concentration of Health Risk Behaviors")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title='Risk Prevalence (%)')
plt.show()



