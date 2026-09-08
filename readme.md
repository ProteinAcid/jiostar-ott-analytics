# OTT Engagement & Recommendation Analytics Platform

An end-to-end analytics platform simulating a streaming service (in the spirit of JioHotstar), built to analyze content performance, power personalized recommendations, evaluate search relevance, and run experimentation — using the real MovieLens dataset as its core, with a synthetic OTT layer engineered on top.

## Problem

Streaming platforms sit on huge amounts of behavioral data — what people watch, search for, and rate — and the job of an analytics team is to turn that into decisions: which content to promote, how to personalize recommendations, whether a new algorithm actually improves engagement, and whether search results are surfacing the right content. This project builds a small but complete version of that pipeline, end to end, on real data.

## Approach

1. **Data foundation**: Loaded the real MovieLens `ml-latest-small` dataset (9,742 movies, 100,836 ratings, 610 users, 3,683 tags) into PostgreSQL (via Supabase), with a normalized schema using composite primary keys and foreign key constraints.
2. **Synthetic OTT layer**: Generated `users`, `watch_events`, and `search_logs` on top of the real MovieLens users — not randomly, but deliberately correlated to real signals already present in the data (e.g. watch completion % is derived from real rating values; subscription tier is weighted by real engagement level; search click-through is rank-weighted and popularity-weighted). This keeps the synthetic layer behaviorally realistic rather than pure noise.
3. **Content & engagement analytics**: Scored content performance (completion rate, drop-off), analyzed retention by subscription tier, and tested for significant differences in watch behavior across devices/tiers.
4. **Recommendation engine**: Built both a content-based recommender (TF-IDF + cosine similarity on genres) and a collaborative filtering recommender (ALS matrix factorization via `implicit`), evaluated with a proper train/test split.
5. **Search relevance**: Measured click-through rate by search result rank, then built and validated a popularity-weighted re-ranking approach.
6. **Experimentation**: Designed and ran a properly-powered A/B test comparing the collaborative filtering recommender against a "trending" baseline.
7. **Dashboard**: Built an interactive Power BI dashboard surfacing all of the above for a content/growth stakeholder audience.

## Tech Stack

Python (pandas, NumPy, Faker) · PostgreSQL (Supabase) · plain SQL · scikit-learn · implicit (ALS) · scipy / statsmodels · Power BI · Git/GitHub

## Key Results

| Analysis | Result |
|---|---|
| Content performance | Identified top-performing titles by completion rate, with near-zero early drop-off for highly-rated content |
| Retention | 7-day and 30-day retention varies by subscription tier (Premium: 44.9% @7d; Basic: 58.4% @30d) |
| Device/tier watch-time test | Statistically significant differences (ANOVA, p<0.001) but small effect sizes (<2 percentage points) — a deliberate finding on statistical vs. practical significance at scale |
| Recommendation engine | Collaborative filtering (ALS) achieved **Precision@10 = 0.181, Recall@10 = 0.197** on held-out ratings (597 evaluable users) |
| Search re-ranking | Popularity-weighted re-ranking improved expected CTR by **+25.5 percentage points (46.6% relative lift)** |
| A/B test | No statistically significant engagement lift from ALS vs. trending baseline (p = 0.487) — an honest null result, discussed below |

## Notable Design Decisions & Honest Limitations

- **Synthetic data is deliberately correlated, not random.** Every synthetic attribute (subscription tier, device, region, watch completion, search behavior) is tied to a real signal in the MovieLens data. This was a conscious choice to avoid meaningless "insights" from pure noise — see `decisions.md` for the full reasoning and every correlation rule used.
- **The A/B test is a retrospective proxy, not a live experiment.** Because `watch_duration_pct` was derived directly from real `rating` values (independent of which algorithm surfaced a movie), there was no causal link built into the data between recommendation source and engagement — so a null result here is expected, not a failure. It demonstrates an important distinction: proxy/retrospective analysis vs. true randomized controlled experiments, which would require live user exposure to measure real causal impact.
- **Precision@10/Recall@10 use a standard 80/20 per-user holdout**, treating held-out ratings ≥4.0 as "relevant" — a common, defensible offline recommender evaluation approach.
- Every mistake, bug, and fix made during development (including several real ones — a broken foreign key, a biased CTR evaluation, a structural overlap bug in the A/B test) is documented transparently in `decisions.md`, rather than hidden.

## How to Run

1. Clone the repo and set up a Python virtual environment
2. Install dependencies: `pip install pandas numpy scikit-learn implicit scipy statsmodels psycopg2-binary sqlalchemy faker jupyter python-dotenv`
3. Create a `.env` file with `DATABASE_URL=<your Postgres connection string>` (not included in this repo for security)
4. Run scripts in order: `load_movielens.py` → `generate_users.py` → `generate_watch_events.py` → `generate_search_logs.py` → analysis scripts in `scripts/`
5. Open the Power BI file to explore the dashboard, or review the CSVs in `data/processed/`

## Project Structure

```
├── data/
│   ├── raw/          # MovieLens source CSVs
│   └── processed/    # Analysis outputs, dashboard exports
├── sql/              # Schema and analysis queries
├── scripts/          # Data generation, analysis, and evaluation scripts
├── dashboard/        # Power BI file
├── decisions.md      # Full log of design decisions, bugs, and fixes
└── README.md
```

## Author

Vedant Ponnanna — built as a resume project tailored to analytics roles in the media/streaming space.