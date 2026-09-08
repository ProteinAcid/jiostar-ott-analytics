from statsmodels.stats.power import TTestIndPower

# assume we want to detect a moderate effect size (Cohen's d = 0.3) in session watch-time,
# with 80% power and 5% significance level -- standard A/B test defaults
analysis = TTestIndPower()
effect_size = 0.3
alpha = 0.05
power = 0.8

sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
print(f"Required sample size per group: {sample_size:.0f}")