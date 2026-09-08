import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with open("sql/03_retention_analysis.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, engine)
print(df)

df.to_csv("data/processed/retention_analysis.csv", index=False)
print("Saved to data/processed/retention_analysis.csv")