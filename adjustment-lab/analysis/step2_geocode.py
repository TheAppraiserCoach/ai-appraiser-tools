"""Step 2 — Geocode all 845 addresses via the Census Bureau bulk geocoder (free, no key)."""
import io
import pandas as pd
import requests

df = pd.read_pickle("df_step1.pkl")

# Build the batch file the Census API expects: id, street, city, state, zip
batch = pd.DataFrame({
    "id": df.index,
    "street": (df["Street #"].fillna("").astype(str).str.strip() + " " +
               df["Street/Road Name"].fillna("").astype(str).str.strip()),
    "city": df["City"].fillna("").str.strip(),
    "state": df["State"].fillna("ID").str.strip(),
    "zip": df["Zip Code"].fillna("").astype(str).str.strip(),
})
buf = io.StringIO()
batch.to_csv(buf, header=False, index=False)

print(f"Submitting {len(batch)} addresses to Census bulk geocoder...")
r = requests.post(
    "https://geocoding.geo.census.gov/geocoder/locations/addressbatch",
    files={"addressFile": ("addresses.csv", buf.getvalue())},
    data={"benchmark": "Public_AR_Current"},
    timeout=600,
)
r.raise_for_status()

res = pd.read_csv(
    io.StringIO(r.text), header=None,
    names=["id", "input_addr", "match", "matchtype", "matched_addr", "coords", "tiger_id", "side"],
)
print("Match status counts:")
print(res["match"].value_counts().to_string())

# split coords "lon,lat"
res = res.set_index("id")
coords = res.loc[res.match == "Match", "coords"].str.split(",", expand=True).astype(float)
df["lon"] = coords[0]
df["lat"] = coords[1]
df["geo_matchtype"] = res["matchtype"]

matched = df["lat"].notna().sum()
print(f"\nGeocoded: {matched}/{len(df)} ({matched/len(df)*100:.1f}%)")
print("Exact vs non-exact:")
print(df.loc[df.lat.notna(), "geo_matchtype"].value_counts().to_string())

# sanity: all coords should be in the Idaho Falls vicinity
in_box = df.lat.between(43.2, 43.8) & df.lon.between(-112.4, -111.6)
print(f"Inside Idaho Falls bounding box: {int(in_box.sum())}/{matched}")
out = df.lat.notna() & ~in_box
if out.sum():
    print("OUTSIDE box (suspect):")
    print(df.loc[out, ["Street #","Street/Road Name","City","lat","lon"]].to_string(index=False))

df.to_pickle("df_step2.pkl")
print("\nsaved df_step2.pkl")
