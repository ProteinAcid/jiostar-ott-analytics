# Project Decisions Log

## Phase 0 — Setup
- Chose Supabase (managed Postgres) over local PostgreSQL install to avoid Windows PATH/setup friction, consistent with Project 1's approach.
- Using plain SQL for all schema/transformation work — no dbt for this project (kept dbt exclusive to Project 1 for tool diversity on resume).
- Development environment: VS Code + Python venv on Windows (PowerShell).

## Phase 1 — Data Layer
- Used the real MovieLens ml-latest-small dataset (9,742 movies, 100,836 ratings, 610 users, 3,683 tags) as the core, real data source — sourced via a GitHub mirror since the official grouplens.org domain wasn't reachable in the dev sandbox.
- Kept the full 610 MovieLens users as the OTT user base (no separate larger synthetic user pool) to keep the project scope manageable.
- Synthetic OTT layer (users, watch_events, search_logs) was NOT randomly generated — each attribute is deliberately correlated to real signals already present in the MovieLens data:
  - `subscription_tier` is weighted by each user's real total rating count (more engaged users skew Premium).
  - `device` and `region` are weighted by whether a user's real rating history skews Action/Sci-Fi.
  - `watch_duration_pct` is derived directly from the real `rating` value (higher rating → higher completion %, plus noise) — verified this produces a near-linear relationship (12% at rating 0.5 → 96% at rating 5.0).
  - `search_logs` click-through is rank-weighted (higher search rank → higher click probability) to simulate realistic CTR decay.
- All schema constraints (composite primary keys, foreign keys) were added explicitly rather than relying on default types — required fixing an early mistake where `users` was auto-created without a primary key by pandas `to_sql`, which broke a downstream foreign key on `watch_events`.
- Final row counts verified: movies 9742, ratings 100836, tags 3683, links 9742, users 610, watch_events 100836, search_logs 4516.

## Phase 2 — Content & Engagement Analytics
- Content performance scoring (avg completion %, early drop-off) confirmed highly-rated classics naturally surfaced with near-zero drop-off — consistent with the rating→completion correlation built into the data.
- Retention analysis (7d/30d by subscription tier) produced non-trivial, non-degenerate numbers despite signup_date and watch_date being generated independently — driven by natural overlap in their date ranges. Noted as a limitation: the pattern isn't strictly monotonic by tier, since no deliberate tier→retention correlation was built in.
- ANOVA on watch_duration_pct across device and subscription_tier came back statistically significant (p<0.001 for both) but with small effect sizes (<2 percentage points between groups) — a direct result of the large sample size (100,836 rows) making trivial differences "significant." Used as a deliberate talking point on statistical vs. practical significance rather than treated as a bug.

## Phase 3 — Recommendation Engine
- Content-based filtering (TF-IDF + cosine similarity on genres) produced sensible, interpretable results (e.g. Toy Story matched with other family/animation titles; The Matrix matched with sci-fi/action thrillers).
- Collaborative filtering (ALS matrix factorization via `implicit`, 50 factors) trained cleanly on the real ratings matrix and produced distinctly different, personalized recommendations per user based on latent taste patterns.
- Evaluated collaborative filtering with an 80/20 per-user train/test split (held-out ratings ≥4.0 treated as "relevant"): achieved Precision@10 = 0.181, Recall@10 = 0.197 across 597 evaluable users — in line with typical benchmarks for this dataset size/algorithm.
- Selected collaborative filtering (ALS) as the "new" algorithm to carry into the Phase 5 A/B test, since it has a measurable precision/recall baseline; content-based filtering will remain as a secondary/cold-start approach in the writeup rather than the A/B test candidate.

## Phase 4 — Search Relevance
- Initial CTR-by-rank analysis showed a clean decay curve (91% CTR at rank 1 down to 15.3% at rank 10), confirming the rank-weighted click probability built into the synthetic data.
- First attempt at popularity-weighted re-ranking showed a *negative* lift (-10%), traced to a real methodology flaw: search targets were originally sampled uniformly at random, independent of popularity, so there was no real signal for a popularity-based re-ranker to exploit — and the initial evaluation only used clicked rows, introducing additional bias.
- Fixed by (1) evaluating on the full search_logs table via a new `searched_movie_id` column (not just clicked rows), and (2) regenerating search logs with popularity-weighted target sampling (using real rating counts) to mimic realistic user search behavior.
- After the fix: popularity-weighted re-ranking achieved a genuine +25.5 percentage point (46.6% relative) lift in expected CTR — a defensible, mechanistically sound result.