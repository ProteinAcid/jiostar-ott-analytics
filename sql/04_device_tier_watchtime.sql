SELECT
    w.device,
    u.subscription_tier,
    w.watch_duration_pct
FROM watch_events w
JOIN users u ON w.user_id = u.user_id;