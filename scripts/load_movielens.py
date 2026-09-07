import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Connect using SQLAlchemy (pandas needs this, not raw psycopg2, for .to_sql)
engine = create_engine(os.getenv("DATABASE_URL"))

# Step 1: Run the schema creation SQL
with open("sql/01_create_tables.sql", "r") as f:
    schema_sql = f.read()

with engine.connect() as conn:
    conn.execute(text(schema_sql))
    conn.commit()
print("Tables created.")

# Step 2: Load each CSV into its table
# Order matters: movies first, since ratings/tags/links have foreign keys pointing to it

movies = pd.read_csv("data/raw/movies.csv")
movies.columns = ["movie_id", "title", "genres"]
movies.to_sql("movies", engine, if_exists="append", index=False)
print(f"Loaded {len(movies)} rows into movies")

ratings = pd.read_csv("data/raw/ratings.csv")
ratings.columns = ["user_id", "movie_id", "rating", "timestamp"]
ratings.to_sql("ratings", engine, if_exists="append", index=False)
print(f"Loaded {len(ratings)} rows into ratings")

tags = pd.read_csv("data/raw/tags.csv")
tags.columns = ["user_id", "movie_id", "tag", "timestamp"]
tags.to_sql("tags", engine, if_exists="append", index=False)
print(f"Loaded {len(tags)} rows into tags")

links = pd.read_csv("data/raw/links.csv")
links.columns = ["movie_id", "imdb_id", "tmdb_id"]
links.to_sql("links", engine, if_exists="append", index=False)
print(f"Loaded {len(links)} rows into links")

print("All data loaded successfully!")