import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
fake = Faker()
np.random.seed(42)

with open("sql/01_create_tables.sql", "r") as f:
    schema_sql = f.read()

with engine.connect() as conn:
    conn.execute(text(schema_sql))
    conn.commit()
print("Schema ensured.")

users = pd.read_sql("SELECT user_id FROM users", engine)
movies = pd.read_sql("SELECT movie_id, title FROM movies", engine)

rows = []
for _, user in users.iterrows():
    num_searches = np.random.randint(1, 15)  # each user searches a few times
    for _ in range(num_searches):
        sampled_movie = movies.sample(1).iloc[0]
        search_query = sampled_movie["title"].split("(")[0].strip()

        result_rank = np.random.randint(1, 11)  # position 1-10 in search results

        # CTR realism: higher rank (closer to 1) = higher chance of click
        click_prob = max(0.9 - (result_rank - 1) * 0.08, 0.05)
        clicked = np.random.random() < click_prob
        clicked_movie_id = sampled_movie["movie_id"] if clicked else None

        search_timestamp = fake.date_time_between(start_date="-1y", end_date="now")

        rows.append({
            "user_id": user["user_id"],
            "search_query": search_query,
            "clicked_movie_id": clicked_movie_id,
            "search_timestamp": search_timestamp,
            "result_rank": result_rank
        })

search_df = pd.DataFrame(rows)
search_df.to_sql("search_logs", engine, if_exists="append", index=False)
print(f"Generated and loaded {len(search_df)} search log entries")