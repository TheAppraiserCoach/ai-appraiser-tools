"""Analytical core for the TrueTracts-style demo app.
Refactors the step1-7 pipeline into reusable functions."""
import io
import re
import pickle
import numpy as np
import pandas as pd
import requests
from pygam import LinearGAM, s, l, f

CENSUS_BATCH = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
CENSUS_ONE = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

NUM_COLS = {
    "Sold Price": "sold_price", "List Price": "list_price",
    "Original List Price": "orig_list_price", "Days on Market": "dom",
    "Bedrooms": "beds", "Bathrooms": "full_baths", "Total Half Baths": "half_baths",
    "Apx Acreage": "acreage", "Apx Year Built": "year_built",
    "Apx Total SqFt": "total_sqft", "Abv Grade SqFt": "abv_sqft",
    "Blw Grade SqFt": "blw_sqft", "Basement SqFt": "bsmt_sqft",
}
MODEL_COLS = ["gla", "acreage", "year_built", "t_days", "beds", "full_baths",
              "half_baths", "bsmt", "garage_spaces", "fireplaces", "patio_deck_ct",
              "has_ac", "hoa", "has_view", "garage_type_code"]
GARAGE_LEVELS = ["None", "Attached", "Detached", "Carport", "Other"]


def _first_int(x, default=0):
    if pd.isna(x):
        return default
    m = re.search(r"\d+", str(x))
    return int(m.group()) if m else default


def load_and_validate(file_like) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(file_like, dtype=str)
    report = {"rows": len(df), "columns": len(df.columns), "issues": [], "missing": {}}
    required = list(NUM_COLS.keys()) + ["Sold Date", "Street #", "Street/Road Name",
                                        "City", "State", "Zip Code"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV is missing required columns: {missing_cols}. "
                         "Export must follow the MLS export recipe.")
    for src, dst in NUM_COLS.items():
        df[dst] = pd.to_numeric(df[src].str.replace(",", "").str.strip(), errors="coerce")
    df["sold_date"] = pd.to_datetime(df["Sold Date"], format="%m/%d/%Y", errors="coerce")

    for c in df.columns[:40]:
        blanks = int(df[c].isna().sum() + (df[c].astype(str).str.strip() == "").sum())
        if blanks:
            report["missing"][c] = blanks

    n = len(df)
    if n < 300:
        report["issues"].append(
            f"Only {n} sales — below the 300 minimum. The model will run but "
            "confidence bands will be wide; treat every adjustment as a rough starting point.")
    bad_price = int(((df.sold_price.isna()) | (df.sold_price <= 0)).sum())
    if bad_price:
        report["issues"].append(f"{bad_price} rows with missing/zero sold price (excluded).")
    bad_date = int(df.sold_date.isna().sum())
    if bad_date:
        report["issues"].append(f"{bad_date} rows with unparseable sold date (excluded).")
    report["date_min"] = str(df.sold_date.min().date()) if df.sold_date.notna().any() else "n/a"
    report["date_max"] = str(df.sold_date.max().date()) if df.sold_date.notna().any() else "n/a"
    report["median_price"] = float(df.sold_price.median())
    return df, report


def geocode_batch(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    batch = pd.DataFrame({
        "id": df.index,
        "street": (df["Street #"].fillna("").astype(str).str.strip() + " " +
                   df["Street/Road Name"].fillna("").astype(str).str.strip()),
        "city": df["City"].fillna("").str.strip(),
        "state": df["State"].fillna("").str.strip(),
        "zip": df["Zip Code"].fillna("").astype(str).str.strip(),
    })
    buf = io.StringIO()
    batch.to_csv(buf, header=False, index=False)
    r = requests.post(CENSUS_BATCH, files={"addressFile": ("a.csv", buf.getvalue())},
                      data={"benchmark": "Public_AR_Current"}, timeout=600)
    r.raise_for_status()
    res = pd.read_csv(io.StringIO(r.text), header=None,
                      names=["id", "in", "match", "mtype", "maddr", "coords", "tid", "side"]
                      ).set_index("id")
    coords = res.loc[res.match == "Match", "coords"].str.split(",", expand=True).astype(float)
    df = df.copy()
    df["lon"] = coords[0]
    df["lat"] = coords[1]
    return df, {"matched": int(df.lat.notna().sum()), "total": len(df)}


def geocode_one(address: str):
    try:
        r = requests.get(CENSUS_ONE, params={"address": address,
                         "benchmark": "Public_AR_Current", "format": "json"}, timeout=30)
        m = r.json()["result"]["addressMatches"]
        if m:
            return m[0]["coordinates"]["y"], m[0]["coordinates"]["x"]
    except Exception:
        pass
    return None, None


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["garage_spaces"] = df.get("Garage # Stalls/Type", pd.Series(index=df.index)).apply(_first_int)
    def gtype(x):
        if pd.isna(x) or str(x).strip() == "":
            return "None"
        xs = str(x)
        for t in ("Attached", "Detached", "Carport"):
            if t in xs:
                return t
        return "Other"
    df["garage_type"] = df.get("Garage # Stalls/Type", pd.Series(index=df.index)).apply(gtype)
    df["fireplaces"] = df.get("Fireplace", pd.Series(index=df.index)).apply(_first_int)
    df["patio_deck_ct"] = df.get("Patio/Deck", pd.Series(index=df.index)).apply(_first_int)
    df["has_ac"] = df.get("Air Conditioning", pd.Series(index=df.index)).fillna("").str.contains("Central").astype(int)
    df["hoa"] = (df.get("HOA", pd.Series(index=df.index)).fillna("No").str.strip() == "Yes").astype(int)
    df["has_view"] = (df.get("View", pd.Series(index=df.index)).fillna("").str.strip() != "").astype(int)
    df["t_days"] = (df["sold_date"] - df["sold_date"].min()).dt.days.astype(float)
    df["gla"] = df["abv_sqft"]
    # repair zero-GLA rows from Main SqFt where possible
    zero = (df["gla"] == 0) | df["gla"].isna()
    if "Main SqFt" in df.columns:
        df.loc[zero, "gla"] = pd.to_numeric(
            df.loc[zero, "Main SqFt"].astype(str).str.replace(",", ""), errors="coerce")
    df["bsmt"] = df["blw_sqft"].fillna(0)
    df["garage_type_code"] = pd.Categorical(df["garage_type"], categories=GARAGE_LEVELS).codes
    df = df.dropna(subset=["sold_price", "sold_date", "gla", "acreage", "year_built",
                           "beds", "full_baths", "half_baths"])
    df = df[df.sold_price > 0]
    return df


def make_terms():
    return (s(0, n_splines=10, constraints="monotonic_inc")
            + s(1, n_splines=10) + s(2, n_splines=10) + s(3, n_splines=10)
            + l(4) + l(5) + l(6) + l(7) + l(8) + l(9) + l(10) + l(11) + l(12) + l(13)
            + f(14))


def fit(m: pd.DataFrame):
    X = m[MODEL_COLS].values.astype(float)
    y = m["sold_price"].values.astype(float)
    gam = LinearGAM(make_terms())
    gam.gridsearch(X, y, lam=np.logspace(-1, 5, 13), progress=False)
    pred = gam.predict(X)
    resid = y - pred
    stats = {
        "r2": float(1 - np.sum(resid**2) / np.sum((y - y.mean())**2)),
        "med_pct_err": float(np.median(np.abs(resid) / y) * 100),
        "resid_std": float(np.std(resid)),
        "n": len(m),
    }
    m = m.copy()
    m["pred"] = pred
    m["resid"] = resid
    return gam, m, stats


# ---------- adjustments / Q&A ----------
SMOOTH_TERMS = {"gla": 0, "acreage": 1, "year_built": 2, "t_days": 3}
LINEAR_TERMS = {"beds": 4, "full_baths": 5, "half_baths": 6, "bsmt": 7,
                "garage_spaces": 8, "fireplaces": 9, "patio_deck_ct": 10,
                "has_ac": 11, "hoa": 12, "has_view": 13}
NICE = {"gla": "Gross living area (above grade sqft)", "acreage": "Lot size (acres)",
        "year_built": "Year built", "t_days": "Market conditions (time)",
        "beds": "Bedroom count", "full_baths": "Full bathrooms", "half_baths": "Half bathrooms",
        "bsmt": "Basement sqft (below grade)", "garage_spaces": "Garage spaces",
        "fireplaces": "Fireplaces", "patio_deck_ct": "Patio/deck features",
        "has_ac": "Central air", "hoa": "HOA", "has_view": "View noted in MLS"}


def smooth_curve(gam, term_i, n=200, width=0.95):
    XX = gam.generate_X_grid(term=term_i, n=n)
    pdep, ci = gam.partial_dependence(term=term_i, X=XX, width=width)
    return XX[:, term_i], pdep, ci


def linear_effect(gam, term_i, width=0.95):
    XX = gam.generate_X_grid(term=term_i, n=100)
    pdep, ci = gam.partial_dependence(term=term_i, X=XX, width=width)
    grid = XX[:, term_i]
    rng = grid.max() - grid.min()
    if rng == 0:
        return 0.0, 0.0, 0.0
    slope = (pdep[-1] - pdep[0]) / rng
    lo = (ci[-1, 0] - ci[0, 0]) / rng
    hi = (ci[-1, 1] - ci[0, 1]) / rng
    return float(slope), float(min(lo, hi)), float(max(lo, hi))


def smooth_slope_range(gam, m, col, lo_q=0.25, hi_q=0.75):
    ti = SMOOTH_TERMS[col]
    grid, pdep, ci = smooth_curve(gam, ti)
    lo, hi = m[col].quantile(lo_q), m[col].quantile(hi_q)
    mask = (grid >= lo) & (grid <= hi)
    slope = np.polyfit(grid[mask], pdep[mask], 1)[0]
    lo_s = np.polyfit(grid[mask], ci[mask, 0], 1)[0]
    hi_s = np.polyfit(grid[mask], ci[mask, 1], 1)[0]
    return float(slope), float(min(lo_s, hi_s)), float(max(lo_s, hi_s)), float(lo), float(hi)


def trailing_12mo_pct(gam, m):
    grid, pdep, _ = smooth_curve(gam, 3)
    med_price = m["sold_price"].median()
    trend = med_price + (pdep - np.interp(m["t_days"].median(), grid, pdep))
    end_v = np.interp(grid.max(), grid, trend)
    start_v = np.interp(grid.max() - 365, grid, trend)
    return float((end_v / start_v - 1) * 100)


# ---------- comp finder ----------
def _term_value(gam, term_i, x):
    """Partial-dependence dollar value of one term at value x."""
    XX = gam.generate_X_grid(term=term_i, n=200)
    pdep = gam.partial_dependence(term=term_i, X=XX)
    return float(np.interp(x, XX[:, term_i], pdep))


def rank_comps(gam, m, subject: dict, n_comps=10, miles_weight=15000.0,
               max_age_days=None):
    """Rank sales by dollar-distance from the subject, using the GAM's own
    partial-dependence curves to convert feature differences into dollars."""
    feat_terms = {**{k: v for k, v in SMOOTH_TERMS.items() if k != "t_days"}, **LINEAR_TERMS}
    g = m.copy()
    if max_age_days:
        g = g[g["t_days"] >= g["t_days"].max() - max_age_days]

    dist = np.zeros(len(g))
    detail = {}
    for col, ti in feat_terms.items():
        if col not in subject or subject[col] is None:
            continue
        sub_v = _term_value(gam, ti, subject[col])
        XX = gam.generate_X_grid(term=ti, n=200)
        pdep = gam.partial_dependence(term=ti, X=XX)
        sale_v = np.interp(g[col].values.astype(float), XX[:, ti], pdep)
        d = np.abs(sale_v - sub_v)
        dist += d
        detail[col] = d

    # geographic distance penalty
    if subject.get("lat") and subject.get("lon") and "lat" in g:
        latr = np.radians(g["lat"].values.astype(float))
        dlat = (g["lat"].values - subject["lat"]) * 69.0
        dlon = (g["lon"].values - subject["lon"]) * 69.0 * np.cos(np.radians(subject["lat"]))
        g["miles"] = np.sqrt(dlat**2 + dlon**2)
        dist += np.nan_to_num(g["miles"].values, nan=np.nanmedian(g["miles"])) * miles_weight
    else:
        g["miles"] = np.nan

    # time-adjust each comp's price to "now" using the time smooth
    tgrid, tpdep, _ = smooth_curve(gam, 3)
    now_v = np.interp(g["t_days"].max(), tgrid, tpdep)
    sale_t = np.interp(g["t_days"].values.astype(float), tgrid, tpdep)
    g["time_adj_price"] = g["sold_price"] + (now_v - sale_t)

    g["dollar_distance"] = dist
    out = g.nsmallest(n_comps, "dollar_distance")
    return out
