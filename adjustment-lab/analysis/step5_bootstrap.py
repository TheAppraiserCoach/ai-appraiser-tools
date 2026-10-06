"""Step 5 — Bootstrap the fireplace adjustment: 200 resamples, refit, percentiles."""
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pygam import LinearGAM, s, l, f

m = pd.read_pickle("df_step3.pkl")
cols = ["gla", "acreage", "year_built", "t_days", "beds", "full_baths", "half_baths",
        "bsmt", "garage_spaces", "fireplaces", "patio_deck_ct", "has_ac", "hoa",
        "has_view", "garage_type_code"]
X = m[cols].values.astype(float)
y = m["sold_price"].values.astype(float)

def make_terms():
    return (s(0, n_splines=10, constraints="monotonic_inc")
            + s(1, n_splines=10) + s(2, n_splines=10) + s(3, n_splines=10)
            + l(4) + l(5) + l(6) + l(7) + l(8) + l(9) + l(10) + l(11) + l(12) + l(13)
            + f(14))

def fireplace_effect(gam):
    XX = gam.generate_X_grid(term=9, n=50)
    pdep = gam.partial_dependence(term=9, X=XX)
    grid = XX[:, 9]
    return (pdep[-1] - pdep[0]) / (grid[-1] - grid[0])  # $ per fireplace

N_BOOT = 200
rng = np.random.default_rng(7)
vals, failed = [], 0
for b in range(N_BOOT):
    idx = rng.integers(0, len(m), len(m))
    try:
        g = LinearGAM(make_terms(), lam=0.1).fit(X[idx], y[idx])
        vals.append(fireplace_effect(g))
    except Exception:
        failed += 1
    if (b + 1) % 50 == 0:
        print(f"  {b+1}/{N_BOOT} resamples done")

vals = np.array(vals)
print(f"\nBOOTSTRAP — fireplace $ adjustment ({len(vals)} successful fits, {failed} failed)")
for p in [10, 25, 50, 75, 90]:
    print(f"  {p}th percentile: ${np.percentile(vals, p):>8,.0f}")
print(f"  mean: ${vals.mean():,.0f} | share of resamples <= $0: {(vals <= 0).mean()*100:.0f}%")

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(vals, bins=30, color="#2c5aa0", edgecolor="white")
for p, c in [(10, "#c62828"), (50, "#2e7d32"), (90, "#c62828")]:
    v = np.percentile(vals, p)
    ax.axvline(v, color=c, ls="--", lw=1.5)
    ax.text(v, ax.get_ylim()[1]*0.95, f" P{p}: ${v:,.0f}", color=c, fontsize=9, rotation=90, va="top")
ax.axvline(0, color="black", lw=1)
ax.set_xlabel("Dollar adjustment per fireplace")
ax.set_ylabel("Bootstrap resamples")
ax.set_title(f"How sure is the fireplace adjustment? ({len(vals)} bootstrap refits, Idaho Falls 2024-2026)")
ax.xaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
plt.tight_layout()
plt.savefig("chart_fireplace_bootstrap.png", dpi=150)
print("saved chart_fireplace_bootstrap.png")
np.save("bootstrap_fireplace.npy", vals)
