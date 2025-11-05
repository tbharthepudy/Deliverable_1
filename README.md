# Deliverable 1 — LEAP Learning  
This repository contains the code for my LEAP Learning deliverable.  
It includes data ingestion and transformation scripts to pull in health-data (via APIs) and load/clean/analyze it using Python and PostgreSQL.

---

## 🗂 Project Structure 
``` 
.
├── ingest.py
├── transform.py
├── .env
├── requirements.txt
└── README.md
```


---

## ⚙️ Setup Instructions  
### 1. Clone the Repository  
```bash
git clone https://github.com/tbharthepudy/Deliverable_1.git  

cd Deliverable_1  
```

### 2. Create & Activate a Virtual Environment
```bash
python3 -m venv my_env  
source my_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt  
```

### 4.Configure Environment Variables - .env file
```
APP_TOKEN=<APP_TOKEN>
POSTGRES_USER=<POSTGRES_USER>
POSTGRES_PASS=<POSTGRES_PASSWORD>
POSTGRES_DB=<POSTGRES_DB>
```
---

## 🚀 Pipeline Overview
### 1. Data Ingestion (ingest.py)
#### This script connects to a public health API, downloads the dataset in chunks, then loads the combined data into a PostgreSQL table (data_table).

### Key steps include:
- Using your API token to fetch large-volume data in paginated requests.
- Concatenating results into a single Pandas DataFrame.
- Extracting longitude/latitude from address if present.
- Writing to Postgres via SQLAlchemy/psycopg2.
 
### 2. Data Transformation & Visualization (transform.py)
#### Once the data is loaded into Postgres, this script reads it, cleans it, performs feature engineering, then generates aggregations and visualizations (e.g., bar charts, heatmaps).

### Transformations include:
- Lower-casing column names and standardizing types.
- Removing system fields and redundant metadata.
- Renaming columns for clarity (e.g., data_value → prevalence_rate, etc.).
- Calculating a derived metric such as:
```python
df['people_with_measure'] = (df['prevalence_rate'] / 100) * df['totalpopulation']
```
### Aggregations include:
- by state/year/health issue, by location, etc.
### Visualization:
- Top States by a Measure 
    - This bar chart highlights the states with the highest average obesity rates across the dataset. It quickly identifies regions with the greatest public health concern regarding obesity levels.
    ![](https://github.com/tbharthepudy/Deliverable_1/blob/dev/create_documentation/assets/top10_states.png)
    
- Lowest States by Another:
    - This horizontal bar plot shows the states reporting the lowest arthritis prevalence. It helps pinpoint regions performing better in joint-health outcomes relative to others.
    ![](https://github.com/tbharthepudy/Deliverable_1/blob/dev/create_documentation/assets/top15_states.png)
    
- Correlation Heatmap:
    - The heatmap visualizes how obesity, smoking, and asthma rates correlate across states. Strong correlations indicate possible co-occurrence or shared health risk factors.
    ![](https://github.com/tbharthepudy/Deliverable_1/blob/dev/create_documentation/assets/correlation.png)
    
- Geographic Scatter:
    - This scatter plot maps risk behaviors (like smoking or binge drinking) across longitude and latitude. It visually reveals geographic clusters where unhealthy behaviors are more concentrated.
    ![](https://github.com/tbharthepudy/Deliverable_1/blob/dev/create_documentation/assets/scatter_plot.png)
    



