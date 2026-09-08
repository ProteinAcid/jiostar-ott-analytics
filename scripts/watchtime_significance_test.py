import os
import pandas as pd
from sqlalchemy import create_engine
from scipy import stats
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with open("sql/04_device_tier_watchtime.sql", "r") as f:
    query = f.read()

df = pd.read_sql(query, engine)

# ANOVA across devices
device_groups = [group["watch_duration_pct"].values for name, group in df.groupby("device")]
f_stat, p_value = stats.f_oneway(*device_groups)
print(f"Device ANOVA: F={f_stat:.2f}, p={p_value:.4f}")

# ANOVA across subscription tiers
tier_groups = [group["watch_duration_pct"].values for name, group in df.groupby("subscription_tier")]
f_stat2, p_value2 = stats.f_oneway(*tier_groups)
print(f"Subscription tier ANOVA: F={f_stat2:.2f}, p={p_value2:.4f}")

print("\nMean watch_duration_pct by device:")
print(df.groupby("device")["watch_duration_pct"].mean())

print("\nMean watch_duration_pct by subscription_tier:")
print(df.groupby("subscription_tier")["watch_duration_pct"].mean())