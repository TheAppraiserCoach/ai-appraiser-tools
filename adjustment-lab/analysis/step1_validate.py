"""Step 1 — Load and validate the Idaho Falls MLS closed-sales CSV."""
import pandas as pd
import numpy as np

import sys
SRC = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"   # your MLS closed-sales export
df = pd.read_csv(SRC, dtype=str)
print(f"ROWS: {len(df)}  COLUMNS: {len(df.columns)}")

# --- numeric conversions ---
num_cols = {
    "Sold Price": "sold_price", "List Price": "list_price",
    "Original List Price": "orig_list_price", "Days on Market": "dom",
    "Bedrooms": "beds", "Bathrooms": "full_baths", "Total Half Baths": "half_baths",
    "Apx Acreage": "acreage", "Apx Year Built": "year_built",
    "Apx Total SqFt": "total_sqft", "Abv Grade SqFt": "abv_sqft",
    "Blw Grade SqFt": "blw_sqft", "Basement SqFt": "bsmt_sqft",
    "HOA Fee Amount": "hoa_fee",
}
for src, dst in num_cols.items():
    df[dst] = pd.to_numeric(df[src].str.replace(",", "").str.strip(), errors="coerce")

df["sold_date"] = pd.to_datetime(df["Sold Date"], format="%m/%d/%Y", errors="coerce")

# --- missing/null report ---
print("\nMISSING / BLANK BY COLUMN (raw):")
for c in df.columns[:39]:  # original columns only
    blanks = df[c].isna().sum() + (df[c].astype(str).str.strip() == "").sum()
    if blanks > 0:
        print(f"  {c:28s} {blanks:4d}  ({blanks/len(df)*100:.0f}%)")

# --- date range ---
print(f"\nSOLD DATE RANGE: {df.sold_date.min().date()} to {df.sold_date.max().date()}")

# --- duplicates ---
print(f"DUPLICATE MLS #: {df['MLS Number'].duplicated().sum()}")

# --- outlier flags ---
print("\nOUTLIER FLAGS:")
flags = {
    "sold_price <= 0 or null": (df.sold_price.isna()) | (df.sold_price <= 0),
    "sold_price < $50k": df.sold_price < 50000,
    "sold_price > $2M": df.sold_price > 2_000_000,
    "GLA (total_sqft) <= 0 or null": (df.total_sqft.isna()) | (df.total_sqft <= 0),
    "GLA < 400 sqft": df.total_sqft < 400,
    "GLA > 10,000 sqft": df.total_sqft > 10000,
    "year_built missing": df.year_built.isna(),
    "year_built < 1860": df.year_built < 1860,
    "beds == 0 or null": (df.beds.isna()) | (df.beds == 0),
    "acreage missing": df.acreage.isna(),
    "acreage > 40": df.acreage > 40,
    "DOM missing": df.dom.isna(),
    "DOM > 365": df.dom > 365,
    "sold date missing": df.sold_date.isna(),
}
for name, mask in flags.items():
    n = int(mask.sum())
    if n:
        print(f"  {name:32s} {n}")

# --- price-vs-GLA sanity: flag price/sqft extremes ---
ok = (df.sold_price > 0) & (df.total_sqft > 400)
ppsf = df.loc[ok, "sold_price"] / df.loc[ok, "total_sqft"]
print(f"\nPRICE/SQFT: median ${ppsf.median():.0f}, 1st pct ${ppsf.quantile(.01):.0f}, 99th pct ${ppsf.quantile(.99):.0f}")
weird = ok & ((df.sold_price / df.total_sqft < 60) | (df.sold_price / df.total_sqft > 500))
print(f"price/sqft <$60 or >$500 (suspect): {int(weird.sum())}")
if weird.sum():
    print(df.loc[weird, ["MLS Number","Street #","Street/Road Name","sold_price","total_sqft","beds","year_built"]].to_string(index=False))

# --- How Sold (financing) breakdown ---
print("\nHOW SOLD (financing):")
print(df["How Sold"].fillna("(blank)").value_counts().to_string())

# --- Seller concessions ---
print("\nSELLER CONC (Y/N only — no $ amount in this export):")
print(df["Seller Conc"].fillna("(blank)").value_counts().to_string())

# --- price summary ---
print(f"\nSOLD PRICE: min ${df.sold_price.min():,.0f} | median ${df.sold_price.median():,.0f} | max ${df.sold_price.max():,.0f}")
print(f"GLA: min {df.total_sqft.min():,.0f} | median {df.total_sqft.median():,.0f} | max {df.total_sqft.max():,.0f}")

df.to_pickle("df_step1.pkl")
print("\nsaved df_step1.pkl")
