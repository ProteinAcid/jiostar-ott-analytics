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

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS watch_events (
            watch_id SERIAL PRIMARY KEY,
            user_id INT,
            movie_id INT,
            watch_date DATE,
            watch_duration_pct NUMERIC(5,2),
            device VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
        );
    """))
    conn.commit()

# base every watch event on a real rating (real user-movie pair)
ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)
users = pd.read_sql("SELECT user_id, subscription_tier, device FROM users", engine)

merged = ratings.merge(users, on="user_id")

rows = []
for _, row in merged.iterrows():
    # higher rating -> higher watch completion (real correlation, not random)
    base_pct = row["rating"] / 5.0 * 100
    noise = np.random.normal(0, 10)
    watch_duration_pct = min(max(base_pct + noise, 5), 100)

    watch_date = fake.date_between(start_date="-1y", end_date="today")

    rows.append({
        "user_id": row["user_id"],
        "movie_id": row["movie_id"],
        "watch_date": watch_date,
        "watch_duration_pct": round(watch_duration_pct, 2),
        "device": row["device"]
    })

watch_df = pd.DataFrame(rows)
watch_df.to_sql("watch_events", engine, if_exists="append", index=False)
print(f"Generated and loaded {len(watch_df)} watch events")