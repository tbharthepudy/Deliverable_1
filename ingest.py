import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://data.cdc.gov/api/v3/views/swc5-untb/query.json"
APP_TOKEN = os.getenv("APP_TOKEN")

limit = 100000
offset = 0
all_chunks = []

while True:
    url = f"{API_BASE}?$limit={limit}&$offset={offset}&$$app_token={APP_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if not data:  # stop when API returns nothing
        break

    df_chunk = pd.DataFrame(data)
    all_chunks.append(df_chunk)

    offset += limit
    print(f"Fetched {len(df_chunk)} records (offset={offset})")

df = pd.concat(all_chunks, ignore_index=True)
print(f"Total records: {len(df)}")


# API_URL = "https://data.cdc.gov/api/v3/views/swc5-untb/query.json?$limit=100000&$$app_token=" + os.getenv("APP_TOKEN")

# response = requests.get(API_URL)
# data = response.json()

# df = pd.DataFrame(data)
# print(df.columns)

df['longitude'] = df['geolocation'].apply(lambda x: x['coordinates'][0] if pd.notnull(x) else None)
df['latitude']  = df['geolocation'].apply(lambda x: x['coordinates'][1] if pd.notnull(x) else None)

df.drop("geolocation", axis=1, inplace=True)

print(df.columns)
print(df.head())
# PostgreSQL connection string format
username = os.getenv('POSTGRES_USER')
password = os.getenv("POSTGRES_PASS")
database = os.getenv("POSTGRES_DB")
engine = create_engine(f"postgresql+psycopg2://{username}:{password}@localhost:5432/{database}")

# Write DataFrame to SQL table
df.to_sql("data_table", engine, if_exists="replace", index=False)

