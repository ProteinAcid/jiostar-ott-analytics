import os
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sqlalchemy import create_engine
import implicit
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)
movies = pd.read_sql("SELECT movie_id, title FROM movies", engine)

# implicit needs integer indices starting at 0, not raw user_id/movie_id values
# so we build lookup mappings between raw IDs and matrix positions
user_ids = ratings["user_id"].unique()
movie_ids = ratings["movie_id"].unique()

user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

ratings["user_idx"] = ratings["user_id"].map(user_to_idx)
ratings["movie_idx"] = ratings["movie_id"].map(movie_to_idx)

# build a sparse matrix: rows = users, columns = movies, values = rating (as "confidence")
user_item_matrix = csr_matrix(
    (ratings["rating"], (ratings["user_idx"], ratings["movie_idx"])),
    shape=(len(user_ids), len(movie_ids))
)

# train the matrix factorization model
model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=20)
model.fit(user_item_matrix)

def recommend_for_user(raw_user_id, top_n=10):
    user_idx = user_to_idx[raw_user_id]
    recommended_idx, scores = model.recommend(
        user_idx, user_item_matrix[user_idx], N=top_n, filter_already_liked_items=True
    )

    result = pd.DataFrame({
        "movie_id": [idx_to_movie[i] for i in recommended_idx],
        "score": scores
    })
    result = result.merge(movies, on="movie_id")
    print(f"\nTop {top_n} recommendations for user {raw_user_id}:")
    print(result[["title", "score"]])
    return result

# test for a couple of users
recommend_for_user(1)
recommend_for_user(50)