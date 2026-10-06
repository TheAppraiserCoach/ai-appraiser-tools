"""Step 3 — Feature engineering + GAM fit (pygam)."""
import re
import numpy as np
import pandas as pd
from pygam import LinearGAM, s, l, f

df = pd.read_pickle("df_step2.pkl")

# ---------- feature engineering from free-text fields ----------
def first_int(x, default=0):
    if pd.isna(x): return default
    m = re.search(r"\d+", str(x))
    return int(m.group()) if m else default

# Garage: "2 Stalls, Attached" -> spaces + type
df["garage_spaces"] = df["Garage # Stalls/Type"].apply(lambda x: first_int(x, 0))
def gtype(x):
    if pd.isna(x) or str(x).strip() == "": return "None"
    xs = str(x)
    if "Attached" in xs: return "Attached"
    if "Detached" in xs: return "Detached"
    if "Carport" in xs: return "Carport"
    return "Other"
df["garage_type"] = df["Garage # Stalls/Type"].apply(gtype)

# Fireplace: "2, Gas" -> count (blank = 0)
df["fireplaces"] = df["Fireplace"].apply(lambda x: first_int(x, 0))

# Patio/Deck: "2, Covered, Deck, Patio" -> count (no sqft available in this export)
df["patio_deck_ct"] = df["Patio/Deck"].apply(lambda x: first_int(x, 0))

# AC / HOA / view
df["has_ac"] = df["Air Conditioning"].fillna("").str.contains("Central").astype(int)
df["hoa"] = (df["HOA"].fillna("No").str.strip() == "Yes").astype(int)
df["has_view"] = (df["View"].fillna("").str.strip() != "").astype(int)  # 93% blank; weak term

# time term: days since first sale
df["t_days"] = (df["sold_date"] - df["sold_date"].min()).dt.days.astype(float)

# GLA = above grade sqft (appraisal convention); basement separately
df["gla"] = df["abv_sqft"]
df["bsmt"] = df["blw_sqft"].fillna(0)

# categorical codes for pygam factor terms
df["garage_type_code"] = pd.Categorical(df["garage_type"],
    categories=["None", "Attached", "Detached", "Carport", "Other"]).codes

# ---------- model matrix ----------
FEATURES = [
    # smooths
    ("gla",            "s"),   # 0
    ("acreage",        "s"),   # 1
    ("year_built",     "s"),   # 2
    ("t_days",         "s"),   # 3  <- market conditions / time
    # linears
    ("beds",           "l"),   # 4
    ("full_baths",     "l"),   # 5
    ("half_baths",     "l"),   # 6
    ("bsmt",           "l"),   # 7
    ("garage_spaces",  "l"),   # 8
    ("fireplaces",     "l"),   # 9
    ("patio_deck_ct",  "l"),   # 10
    ("has_ac",         "l"),   # 11
    ("hoa",            "l"),   # 12
    ("has_view",       "l"),   # 13
    # factor
    ("garage_type_code", "f"), # 14
]
cols = [c for c, _ in FEATURES]
m = df.dropna(subset=["sold_price", "gla", "acreage", "year_built", "t_days",
                      "beds", "full_baths", "half_baths"]).copy()
print(f"Modeling rows: {len(m)} of {len(df)} (dropped {len(df)-len(m)} with missing core fields)")

X = m[cols].values.astype(float)
y = m["sold_price"].values.astype(float)

terms = s(0) + s(1) + s(2) + s(3)
for i, (_, kind) in enumerate(FEATURES):
    if kind == "l": terms += l(i)
    elif kind == "f": terms += f(i)

gam = LinearGAM(terms)
gam.gridsearch(X, y, progress=False)   # tunes smoothing penalties

# ---------- fit statistics ----------
pred = gam.predict(X)
resid = y - pred
ss_res = np.sum(resid**2); ss_tot = np.sum((y - y.mean())**2)
r2 = 1 - ss_res/ss_tot
print(f"\nFIT STATISTICS")
print(f"  R^2 (in-sample):        {r2:.3f}")
print(f"  Pseudo R^2 (expl dev):  {gam.statistics_['pseudo_r2']['explained_deviance']:.3f}")
print(f"  Residual std:           ${np.std(resid):,.0f}")
print(f"  Median abs error:       ${np.median(np.abs(resid)):,.0f}")
print(f"  Median abs % error:     {np.median(np.abs(resid)/y)*100:.1f}%")
print(f"  Effective DoF:          {gam.statistics_['edof']:.1f}")

# 5-fold cross-validation for honest out-of-sample error
from numpy.random import default_rng
rng = default_rng(42)
idx = rng.permutation(len(m)); folds = np.array_split(idx, 5)
cv_err = []
for k in range(5):
    test = folds[k]; train = np.concatenate([folds[j] for j in range(5) if j != k])
    g = LinearGAM(terms).gridsearch(X[train], y[train], progress=False)
    cv_err.append(np.median(np.abs(g.predict(X[test]) - y[test]) / y[test]))
print(f"  5-fold CV median abs % error: {np.mean(cv_err)*100:.1f}%")

m["resid"] = resid
m["pred"] = pred
m.to_pickle("df_step3.pkl")
import pickle
with open("gam_model.pkl", "wb") as fh:
    pickle.dump({"gam": gam, "features": FEATURES, "cols": cols}, fh)
print("\nsaved df_step3.pkl + gam_model.pkl")
