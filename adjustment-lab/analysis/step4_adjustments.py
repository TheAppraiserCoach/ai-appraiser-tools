"""Step 4 — Extract marginal dollar adjustments per feature, with 95% confidence ranges."""
import pickle
import numpy as np
import pandas as pd

m = pd.read_pickle("df_step3.pkl")
with open("gam_model.pkl", "rb") as fh:
    saved = pickle.load(fh)
gam, FEATURES, cols = saved["gam"], saved["features"], saved["cols"]

X = m[cols].values.astype(float)

def smooth_slope(term_i, col, lo_q=0.25, hi_q=0.75):
    """Average $/unit slope of a smooth term across the interquartile range, with CI."""
    XX = gam.generate_X_grid(term=term_i, n=200)
    pdep, ci = gam.partial_dependence(term=term_i, X=XX, width=0.95)
    grid = XX[:, term_i]
    lo, hi = m[col].quantile(lo_q), m[col].quantile(hi_q)
    mask = (grid >= lo) & (grid <= hi)
    g, p = grid[mask], pdep[mask]
    slope = np.polyfit(g, p, 1)[0]
    lo_s = np.polyfit(g, ci[mask, 0], 1)[0]
    hi_s = np.polyfit(g, ci[mask, 1], 1)[0]
    return slope, min(lo_s, hi_s), max(lo_s, hi_s), lo, hi

def linear_effect(term_i):
    """Per-unit $ effect of a linear term, with CI, from partial dependence."""
    XX = gam.generate_X_grid(term=term_i, n=100)
    pdep, ci = gam.partial_dependence(term=term_i, X=XX, width=0.95)
    grid = XX[:, term_i]
    rng = grid.max() - grid.min()
    if rng == 0: return 0, 0, 0
    slope = (pdep[-1] - pdep[0]) / rng
    lo = (ci[-1, 0] - ci[0, 0]) / rng
    hi = (ci[-1, 1] - ci[0, 1]) / rng
    return slope, min(lo, hi), max(lo, hi)

rows = []

# GLA $/sqft (smooth): slope over the middle of the market
sl, lo, hi, a, b = smooth_slope(0, "gla")
rows.append(("GLA ($/sqft above grade)", f"${sl:,.0f}", f"${lo:,.0f} to ${hi:,.0f}", f"slope measured {a:,.0f}-{b:,.0f} sqft"))

# Acreage (smooth): $ per 0.1 acre in typical range
sl, lo, hi, a, b = smooth_slope(1, "acreage")
rows.append(("Lot size ($ per 0.1 acre)", f"${sl*0.1:,.0f}", f"${lo*0.1:,.0f} to ${hi*0.1:,.0f}", f"slope measured {a:.2f}-{b:.2f} ac"))

# Year built (smooth): $ per year of age
sl, lo, hi, a, b = smooth_slope(2, "year_built")
rows.append(("Year built ($ per year newer)", f"${sl:,.0f}", f"${lo:,.0f} to ${hi:,.0f}", f"slope measured {a:.0f}-{b:.0f}"))

# Time (smooth): market conditions — % per year at the end of the window
XX = gam.generate_X_grid(term=3, n=200)
pdep, ci = gam.partial_dependence(term=3, X=XX, width=0.95)
grid = XX[:, 3]
last365 = grid >= (grid.max() - 365)
tslope = np.polyfit(grid[last365], pdep[last365], 1)[0] * 365
med_price = m["sold_price"].median()
rows.append(("Market conditions (last 12 mo)", f"${tslope:,.0f}/yr ({tslope/med_price*100:+.1f}%/yr)", "see trend chart", "time smooth, trailing 365 days"))

linear_names = {
    4: ("Bedroom (each)", 1), 5: ("Full bath (each)", 1), 6: ("Half bath (each)", 1),
    7: ("Basement ($/sqft below grade)", 1), 8: ("Garage space (each)", 1),
    9: ("Fireplace (each)", 1), 10: ("Patio/deck feature (each)", 1),
    11: ("Central air (yes vs no)", 1), 12: ("HOA (yes vs no)", 1),
    13: ("View noted in MLS (yes vs no)", 1),
}
for ti, (name, mult) in linear_names.items():
    slp, lo, hi = linear_effect(ti)
    rows.append((name, f"${slp*mult:,.0f}", f"${lo*mult:,.0f} to ${hi*mult:,.0f}", ""))

# Garage type (factor): level effects vs 'None'
XX = gam.generate_X_grid(term=14, n=5)
pdep, ci = gam.partial_dependence(term=14, X=XX, width=0.95)
levels = ["None", "Attached", "Detached", "Carport", "Other"]
base = pdep[0]
for i, lv in enumerate(levels):
    if i == 0: continue
    n_in_lv = int((m["garage_type"] == lv).sum())
    rows.append((f"Garage type: {lv} vs None", f"${pdep[i]-base:,.0f}",
                 f"${ci[i,0]-base:,.0f} to ${ci[i,1]-base:,.0f}", f"n={n_in_lv}"))

tab = pd.DataFrame(rows, columns=["Feature", "Adjustment", "95% range", "Note"])
print(tab.to_string(index=False))
tab.to_csv("adjustment_table.csv", index=False)
print("\nsaved adjustment_table.csv")
