SELECT
    m.movie_id,
    m.title,
    m.genres,
    COUNT(w.watch_id) AS total_watches,
    ROUND(AVG(w.watch_duration_pct), 1) AS avg_completion_pct,
    ROUND(100.0 * SUM(CASE WHEN w.watch_duration_pct < 20 THEN 1 ELSE 0 END) / COUNT(w.watch_id), 1) AS early_dropoff_pct
FROM movies m
JOIN watch_events w ON m.movie_id = w.movie_id
GROUP BY m.movie_id, m.title, m.genres
HAVING COUNT(w.watch_id) >= 10
ORDER BY avg_completion_pct DESC
LIMIT 20;