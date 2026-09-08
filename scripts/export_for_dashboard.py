import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

os.makedirs("data/processed", exist_ok=True)

tables_to_export = ["movies", "users", "watch_events", "search_logs", "ratings"]

for table in tables_to_export:
    df = pd.read_sql(f"SELECT * FROM {table}", engine)
    path = f"data/processed/{table}.csv"
    df.to_csv(path, index=False)
    print(f"Exported {table} -> {path} ({len(df)} rows)")

print("All tables exported for Power BI.")