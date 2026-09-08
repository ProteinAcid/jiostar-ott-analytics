import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
np.random.seed(42)

popularity = pd.read_sql("""
    SELECT movie_id, COUNT(*) AS num_ratings
    FROM ratings
    GROUP BY movie_id
""", engine)

search_logs = pd.read_sql("SELECT * FROM search_logs", engine)

ctr_by_rank = pd.read_sql("""
    SELECT
        result_rank,
        ROUND(100.0 * SUM(CASE WHEN clicked_movie_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ctr_pct
    FROM search_logs
    GROUP BY result_rank
""", engine)
ctr_lookup = dict(zip(ctr_by_rank["result_rank"], ctr_by_rank["ctr_pct"]))

# baseline: expected CTR at the ORIGINAL rank, for every search (not just clicked ones)
search_logs["baseline_expected_ctr"] = search_logs["result_rank"].map(ctr_lookup)

movies_pop = popularity.set_index("movie_id")["num_ratings"].to_dict()
all_movie_ids = list(movies_pop.keys())

new_ranks = []
for _, row in search_logs.iterrows():
    target_movie = row["searched_movie_id"]  # every search has one, click or not

    competitors = np.random.choice(all_movie_ids, size=9, replace=False)
    candidate_set = list(competitors) + [target_movie]
    candidate_pop = [(mid, movies_pop.get(mid, 0)) for mid in candidate_set]

    candidate_pop.sort(key=lambda x: x[1], reverse=True)
    new_rank = [i for i, (mid, _) in enumerate(candidate_pop, start=1) if mid == target_movie][0]
    new_ranks.append(new_rank)

search_logs["new_rank"] = new_ranks
search_logs["new_expected_ctr"] = search_logs["new_rank"].map(ctr_lookup)

baseline_avg = search_logs["baseline_expected_ctr"].mean()
new_avg = search_logs["new_expected_ctr"].mean()
lift = new_avg - baseline_avg
lift_pct = (lift / baseline_avg) * 100

print(f"Baseline avg expected CTR: {baseline_avg:.2f}%")
print(f"Popularity-reranked avg expected CTR: {new_avg:.2f}%")
print(f"Absolute lift: {lift:.2f} percentage points")
print(f"Relative lift: {lift_pct:.1f}%")