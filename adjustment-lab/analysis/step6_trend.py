"""Step 6 — Market trend: sales scatter, GAM time-term trendline, 12-mo % change."""
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

m = pd.read_pickle("df_step3.pkl")
with open("gam_model.pkl", "rb") as fh:
    saved = pickle.load(fh)
gam, cols = saved["gam"], saved["cols"]

# GAM time term -> trend for the *typical* home (all else held constant)
XX = gam.generate_X_grid(term=3, n=200)
pdep = gam.partial_dependence(term=3, X=XX)
tgrid = XX[:, 3]
dates = m["sold_date"].min() + pd.to_timedelta(tgrid, unit="D")
med_price = m["sold_price"].median()
trend = med_price + (pdep - np.interp(m["t_days"].median(), tgrid, pdep))

# 12-month % change (last 365 days of the window)
end_val = np.interp(tgrid.max(), tgrid, trend)
start_val = np.interp(tgrid.max() - 365, tgrid, trend)
pct12 = (end_val / start_val - 1) * 100

# monthly medians as a second, model-free reference
mm = m.set_index("sold_date").resample("ME")["sold_price"].agg(["median", "count"])

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(m["sold_date"], m["sold_price"], s=14, alpha=0.35, color="#888", label="Individual sales")
ax.plot(mm.index, mm["median"], "o-", color="#b58500", lw=1.2, ms=4, alpha=0.85, label="Monthly median (raw)")
ax.plot(dates, trend, color="#2c5aa0", lw=3, label="GAM time trend (quality-controlled)")
ax.annotate(f"12-month change: {pct12:+.1f}%",
            xy=(dates[-1], trend[-1]), xytext=(-230, 60), textcoords="offset points",
            fontsize=13, fontweight="bold", color="#2c5aa0",
            arrowprops=dict(arrowstyle="->", color="#2c5aa0"))
ax.set_ylim(0, 1_000_000)
ax.yaxis.set_major_formatter(lambda x, _: f"${x/1000:,.0f}k")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Idaho Falls market trend — 845 closed sales, Jul 2024 to Jul 2026")
ax.set_ylabel("Sold price")
ax.legend(loc="upper left")
ax.text(0.99, 0.01, "GAM trend = price movement for a constant-quality home; raw medians move with the mix of what sold",
        transform=ax.transAxes, ha="right", fontsize=8, color="#666")
plt.tight_layout()
plt.savefig("chart_market_trend.png", dpi=150)
print(f"12-month constant-quality change: {pct12:+.1f}%")
print(f"raw monthly median, first 3 mo avg: ${mm['median'].iloc[:3].mean():,.0f} -> last 3 mo avg: ${mm['median'].iloc[-3:].mean():,.0f}")
print("saved chart_market_trend.png")
