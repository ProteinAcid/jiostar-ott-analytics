import os
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sqlalchemy import create_engine
import implicit
from scipy import stats
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
np.random.seed(42)

ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)
watch_events = pd.read_sql("SELECT user_id, movie_id, watch_duration_pct FROM watch_events", engine)

# hold out 20% of each user's ratings -- these represent "unseen" movies the model must predict
ratings["is_test"] = False
for user_id, group in ratings.groupby("user_id"):
    n_test = max(1, int(len(group) * 0.2))
    test_idx = np.random.choice(group.index, size=n_test, replace=False)
    ratings.loc[test_idx, "is_test"] = True

train = ratings[~ratings["is_test"]]

all_users = ratings["user_id"].unique()
np.random.shuffle(all_users)
split_point = len(all_users) // 2
control_users = set(all_users[:split_point])
treatment_users = set(all_users[split_point:])

user_to_idx = {uid: i for i, uid in enumerate(all_users)}
movie_ids = train["movie_id"].unique()
movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}

train["user_idx"] = train["user_id"].map(user_to_idx)
train["movie_idx"] = train["movie_id"].map(movie_to_idx)

user_item_matrix = csr_matrix(
    (train["rating"], (train["user_idx"], train["movie_idx"])),
    shape=(len(all_users), len(movie_ids))
)

model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=20)
model.fit(user_item_matrix)

trending_movies = set(
    watch_events.groupby("movie_id").size().sort_values(ascending=False).head(10).index
)

def get_als_recommendations(user_id, top_n=10):
    user_idx = user_to_idx[user_id]
    recommended_idx, _ = model.recommend(
        user_idx, user_item_matrix[user_idx], N=top_n, filter_already_liked_items=True
    )
    return set(idx_to_movie[i] for i in recommended_idx)

results = []
for user_id in all_users:
    user_watch = watch_events[watch_events["user_id"] == user_id]
    if len(user_watch) == 0:
        continue

    if user_id in control_users:
        relevant_set = trending_movies
        group = "control"
    else:
        relevant_set = get_als_recommendations(user_id)
        group = "treatment"

    matching_watches = user_watch[user_watch["movie_id"].isin(relevant_set)]
    avg_watch_pct = matching_watches["watch_duration_pct"].mean() if len(matching_watches) > 0 else np.nan

    if not np.isnan(avg_watch_pct):
        results.append({"user_id": user_id, "group": group, "avg_watch_pct": avg_watch_pct})

results_df = pd.DataFrame(results)

control_vals = results_df[results_df["group"] == "control"]["avg_watch_pct"]
treatment_vals = results_df[results_df["group"] == "treatment"]["avg_watch_pct"]

print(f"Control group (n={len(control_vals)}): mean watch% = {control_vals.mean():.2f}")
print(f"Treatment group (n={len(treatment_vals)}): mean watch% = {treatment_vals.mean():.2f}")

if len(treatment_vals) > 1 and len(control_vals) > 1:
    t_stat, p_value = stats.ttest_ind(treatment_vals, control_vals, equal_var=False)
    print(f"Lift: {treatment_vals.mean() - control_vals.mean():.2f} percentage points")
    print(f"T-statistic: {t_stat:.3f}, p-value: {p_value:.4f}")
else:
    print("Not enough data in one group to run t-test")

results_df.to_csv("data/processed/ab_test_results.csv", index=False)