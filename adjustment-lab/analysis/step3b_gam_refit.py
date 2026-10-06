"""Step 3b — Refit: repair the zero-GLA row, tame the smooths, constrain GLA monotonic."""
import pickle
import numpy as np
import pandas as pd
from pygam import LinearGAM, s, l, f

m = pd.read_pickle("df_step3.pkl")

# repair the one zero-GLA row (main-floor sqft is the real above-grade area)
bad = m["gla"] == 0
m.loc[bad, "gla"] = pd.to_numeric(m.loc[bad, "Main SqFt"], errors="coerce")
print(f"repaired {int(bad.sum())} zero-GLA row(s)")

cols = ["gla", "acreage", "year_built", "t_days", "beds", "full_baths", "half_baths",
        "bsmt", "garage_spaces", "fireplaces", "patio_deck_ct", "has_ac", "hoa",
        "has_view", "garage_type_code"]
X = m[cols].values.astype(float)
y = m["sold_price"].values.astype(float)

# GLA: monotonic increasing, modest spline budget. Others: modest splines,
# penalty grid that allows real smoothness (up to 1e5) instead of bottoming out at wiggle.
terms = (s(0, n_splines=10, constraints="monotonic_inc")
         + s(1, n_splines=10) + s(2, n_splines=10) + s(3, n_splines=10)
         + l(4) + l(5) + l(6) + l(7) + l(8) + l(9) + l(10) + l(11) + l(12) + l(13)
         + f(14))

gam = LinearGAM(terms)
gam.gridsearch(X, y, lam=np.logspace(-1, 5, 13), progress=False)

pred = gam.predict(X)
resid = y - pred
r2 = 1 - np.sum(resid**2) / np.sum((y - y.mean())**2)
print(f"R^2: {r2:.3f} | median abs % err: {np.median(np.abs(resid)/y)*100:.1f}% | resid std ${np.std(resid):,.0f}")
print("lambdas chosen:", [f"{t.lam[0]:.3g}" for t in gam.terms if hasattr(t, 'lam') and t.lam])

# sanity-print the GLA smooth
XX = gam.generate_X_grid(term=0, n=10)
pdep = gam.partial_dependence(term=0, X=XX)
print("\nGLA smooth (should rise monotonically):")
for g, p in zip(XX[:, 0], pdep):
    print(f"  {g:7,.0f} sqft -> ${p:12,.0f}")

# 5-fold CV
rng = np.random.default_rng(42)
idx = rng.permutation(len(m)); folds = np.array_split(idx, 5)
cv = []
for k in range(5):
    te = folds[k]; tr = np.concatenate([folds[j] for j in range(5) if j != k])
    g2 = LinearGAM(terms).gridsearch(X[tr], y[tr], lam=np.logspace(-1, 5, 7), progress=False)
    cv.append(np.median(np.abs(g2.predict(X[te]) - y[te]) / y[te]))
print(f"\n5-fold CV median abs % error: {np.mean(cv)*100:.1f}%")

m["resid"] = resid
m["pred"] = pred
m.to_pickle("df_step3.pkl")
FEATURES = cols
with open("gam_model.pkl", "wb") as fh:
    pickle.dump({"gam": gam, "features": FEATURES, "cols": cols,
                 "terms_spec": "s(0,mono,10)+s(1,10)+s(2,10)+s(3,10)+l(4..13)+f(14)"}, fh)
print("saved updated df_step3.pkl + gam_model.pkl")
