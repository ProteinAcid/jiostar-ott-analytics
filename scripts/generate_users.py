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

# Run the full schema file (creates movies, ratings, tags, links, users, watch_events)
with open("sql/01_create_tables.sql", "r") as f:
    schema_sql = f.read()

with engine.connect() as conn:
    conn.execute(text(schema_sql))
    conn.commit()
print("Schema created.")

ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)
movies = pd.read_sql("SELECT movie_id, genres FROM movies", engine)

merged = ratings.merge(movies, on="movie_id")

user_activity = merged.groupby("user_id").size().reset_index(name="total_ratings")

def is_action_scifi_fan(genre_string_list):
    combined = " ".join(genre_string_list)
    return ("Action" in combined) or ("Sci-Fi" in combined)

genre_check = merged.groupby("user_id")["genres"].apply(list).reset_index()
genre_check["is_action_scifi_fan"] = genre_check["genres"].apply(is_action_scifi_fan)

user_profile = user_activity.merge(genre_check[["user_id", "is_action_scifi_fan"]], on="user_id")

rows = []
for _, row in user_profile.iterrows():
    user_id = row["user_id"]

    if row["total_ratings"] > 150:
        subscription_tier = np.random.choice(["Premium", "Basic", "Free"], p=[0.7, 0.2, 0.1])
    elif row["total_ratings"] > 50:
        subscription_tier = np.random.choice(["Premium", "Basic", "Free"], p=[0.3, 0.5, 0.2])
    else:
        subscription_tier = np.random.choice(["Premium", "Basic", "Free"], p=[0.1, 0.3, 0.6])

    if row["is_action_scifi_fan"]:
        device = np.random.choice(["Mobile", "TV", "Laptop"], p=[0.6, 0.25, 0.15])
        region = np.random.choice(["Urban", "Suburban", "Rural"], p=[0.65, 0.25, 0.10])
    else:
        device = np.random.choice(["Mobile", "TV", "Laptop"], p=[0.35, 0.35, 0.30])
        region = np.random.choice(["Urban", "Suburban", "Rural"], p=[0.4, 0.4, 0.20])

    signup_date = fake.date_between(start_date="-2y", end_date="-30d")

    rows.append({
        "user_id": user_id,
        "signup_date": signup_date,
        "region": region,
        "device": device,
        "subscription_tier": subscription_tier
    })

users_df = pd.DataFrame(rows)
users_df.to_sql("users", engine, if_exists="append", index=False)
print(f"Generated and loaded {len(users_df)} synthetic user profiles")