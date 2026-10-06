"""Step 7 — Spatial residual map: each sale colored by GAM residual (location signal)."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import folium

m = pd.read_pickle("df_step3.pkl")
g = m.dropna(subset=["lat", "lon"]).copy()
print(f"mappable sales: {len(g)} of {len(m)}")

# cap color scale at +/- $75k so a few extremes don't wash out the map
cap = 75000
g["resid_c"] = g["resid"].clip(-cap, cap)

# ---------- interactive folium map ----------
fmap = folium.Map(location=[g.lat.mean(), g.lon.mean()], zoom_start=12, tiles="cartodbpositron")
def color(v):
    x = (v + cap) / (2 * cap)  # 0..1
    r = int(255 * min(1, 2 * x)); b = int(255 * min(1, 2 * (1 - x)))
    gg = int(80 * (1 - abs(2 * x - 1)))
    return f"#{r:02x}{gg:02x}{b:02x}"
for _, row in g.iterrows():
    folium.CircleMarker(
        location=[row.lat, row.lon], radius=5,
        color=None, fill=True, fill_color=color(row.resid_c), fill_opacity=0.75,
        tooltip=(f"{row['Street #']} {row['Street/Road Name']} — sold ${row.sold_price:,.0f}, "
                 f"model ${row.pred:,.0f}, resid {row.resid:+,.0f}"),
    ).add_to(fmap)
legend = ('<div style="position:fixed;bottom:20px;left:20px;z-index:9999;background:white;'
          'padding:10px 14px;border:1px solid #999;border-radius:6px;font-size:13px">'
          '<b>Sold vs. model prediction</b><br>'
          '<span style="color:#ff5000">&#9679;</span> sold above prediction (location premium)<br>'
          '<span style="color:#0050ff">&#9679;</span> sold below prediction (location discount)<br>'
          f'scale capped at &plusmn;${cap:,}</div>')
fmap.get_root().html.add_child(folium.Element(legend))
fmap.save("map_residuals.html")
print("saved map_residuals.html (interactive, real map tiles)")

# ---------- PNG fallback ----------
fig, ax = plt.subplots(figsize=(10, 9))
sc = ax.scatter(g.lon, g.lat, c=g.resid_c, cmap="coolwarm", s=26, alpha=0.8,
                vmin=-cap, vmax=cap, edgecolors="none")
cb = plt.colorbar(sc, ax=ax, shrink=0.8)
cb.set_label("Residual: sold price minus feature-based prediction ($)")
cb.ax.yaxis.set_major_formatter(lambda x, _: f"${x/1000:,.0f}k")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.set_title(f"Location value isolated from features — {len(g)} geocoded sales, Idaho Falls")
ax.set_aspect(1 / np.cos(np.radians(g.lat.mean())))
plt.tight_layout()
plt.savefig("chart_residual_map.png", dpi=150)
print("saved chart_residual_map.png (PNG fallback)")

# ---------- neighborhood-level summary: where does the model over/under-predict? ----------
sub = (m.groupby(m["Subdivision"].str.strip())
         .agg(n=("resid", "size"), med_resid=("resid", "median"))
         .query("n >= 6").sort_values("med_resid"))
print("\nSubdivisions with consistent location signal (n>=6):")
print("  UNDER-performing (sell below feature value):")
print(sub.head(5).to_string())
print("  OVER-performing (sell above feature value):")
print(sub.tail(5).to_string())
