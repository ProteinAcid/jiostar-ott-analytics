WITH user_activity AS (
    SELECT
        u.user_id,
        u.signup_date,
        u.subscription_tier,
        w.watch_date,
        (w.watch_date - u.signup_date) AS days_since_signup
    FROM users u
    JOIN watch_events w ON u.user_id = w.user_id
    WHERE w.watch_date >= u.signup_date
)
SELECT
    subscription_tier,
    COUNT(DISTINCT user_id) AS total_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 0 AND 7 THEN user_id END) AS active_within_7d,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 0 AND 30 THEN user_id END) AS active_within_30d,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 0 AND 7 THEN user_id END) / COUNT(DISTINCT user_id), 1) AS retention_7d_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 0 AND 30 THEN user_id END) / COUNT(DISTINCT user_id), 1) AS retention_30d_pct
FROM user_activity
GROUP BY subscription_tier
ORDER BY retention_30d_pct DESC;