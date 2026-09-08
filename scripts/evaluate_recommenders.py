import os
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sqlalchemy import create_engine
import implicit
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
np.random.seed(42)

ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)

# train/test split: hold out 20% of each user's ratings to test against
# "held out" ratings simulate movies the user actually liked but we pretend we don't know about
ratings["is_test"] = False
for user_id, group in ratings.groupby("user_id"):
    n_test = max(1, int(len(group) * 0.2))
    test_idx = np.random.choice(group.index, size=n_test, replace=False)
    ratings.loc[test_idx, "is_test"] = True

train = ratings[~ratings["is_test"]]
test = ratings[ratings["is_test"]]

# only count a held-out movie as "relevant" if the user actually rated it highly (>= 4.0)
test_relevant = test[test["rating"] >= 4.0]

user_ids = train["user_id"].unique()
movie_ids = train["movie_id"].unique()
user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

train["user_idx"] = train["user_id"].map(user_to_idx)
train["movie_idx"] = train["movie_id"].map(movie_to_idx)

user_item_matrix = csr_matrix(
    (train["rating"], (train["user_idx"], train["movie_idx"])),
    shape=(len(user_ids), len(movie_ids))
)

model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=20)
model.fit(user_item_matrix)

K = 10
precisions = []
recalls = []

for user_id in user_ids:
    user_idx = user_to_idx[user_id]

    relevant_movies = set(test_relevant[test_relevant["user_id"] == user_id]["movie_id"])
    if len(relevant_movies) == 0:
        continue  # skip users with no relevant held-out movies -- can't evaluate them fairly

    recommended_idx, scores = model.recommend(
        user_idx, user_item_matrix[user_idx], N=K, filter_already_liked_items=True
    )
    recommended_movies = set(idx_to_movie[i] for i in recommended_idx)

    hits = len(recommended_movies & relevant_movies)
    precision = hits / K
    recall = hits / len(relevant_movies)

    precisions.append(precision)
    recalls.append(recall)

print(f"Evaluated on {len(precisions)} users")
print(f"Precision@{K}: {np.mean(precisions):.3f}")
print(f"Recall@{K}: {np.mean(recalls):.3f}")