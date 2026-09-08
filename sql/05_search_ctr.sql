SELECT
    result_rank,
    COUNT(*) AS total_impressions,
    SUM(CASE WHEN clicked_movie_id IS NOT NULL THEN 1 ELSE 0 END) AS total_clicks,
    ROUND(100.0 * SUM(CASE WHEN clicked_movie_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ctr_pct
FROM search_logs
GROUP BY result_rank
ORDER BY result_rank;