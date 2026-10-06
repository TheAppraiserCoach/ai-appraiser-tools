"""TrueTracts-style demo — upload an MLS CSV, get adjustments, trend, map, comps.
Built with Claude Code + Fable 5 for The Appraiser Coach."""
import os
import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import folium
import streamlit.components.v1 as components

import core

st.set_page_config(page_title="Adjustment Lab — The Appraiser Coach",
                   page_icon="📐", layout="wide")

PASSWORD = os.environ.get("APP_PASSWORD", "appraiser2026")   # set APP_PASSWORD in your environment to change it

# ---------- password gate ----------
if "authed" not in st.session_state:
    st.session_state.authed = False
if not st.session_state.authed:
    st.title("📐 Adjustment Lab")
    st.caption("Market-derived adjustments from your own MLS data · The Appraiser Coach")
    pw = st.text_input("Password", type="password")
    if st.button("Enter") or pw:
        if pw == PASSWORD:
            st.session_state.authed = True
            st.rerun()
        elif pw:
            st.error("Wrong password.")
    st.stop()

st.title("📐 Adjustment Lab")
st.caption("Upload your MLS closed-sales export → market-derived adjustments, trend, "
           "location map, and comp selection. Analytical aid — not an appraisal, "
           "not a substitute for your judgment or USPAP obligations.")

# ---------- data input ----------
with st.sidebar:
    st.header("1 · Your data")
    up = st.file_uploader("MLS closed-sales CSV (per the export recipe)", type=["csv", "CSV"])
    DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", "df_step3.pkl")   # not included in the public repo (MLS data); upload your own export
    use_demo = os.path.exists(DEMO_PATH) and st.checkbox("Use demo dataset", value=up is None)
    st.markdown("---")
    st.markdown("**Pipeline:** validate → geocode (US Census) → fit GAM → adjustments")
    st.markdown("Data never leaves this server. Geocoding sends addresses only "
                "(no prices) to the US Census Bureau's free geocoder.")


@st.cache_resource(show_spinner=False)
def run_pipeline(file_bytes: bytes | None, demo: bool):
    import io
    if demo:
        demo_path = os.path.join(os.path.dirname(__file__), "..", "df_step3.pkl")
        m = pd.read_pickle(demo_path)
        report = {"rows": len(m), "issues": [],
                  "date_min": str(m.sold_date.min().date()),
                  "date_max": str(m.sold_date.max().date()),
                  "median_price": float(m.sold_price.median()), "missing": {}}
        geo = {"matched": int(m.lat.notna().sum()), "total": len(m)}
        gam, m, stats = core.fit(m)
        return gam, m, stats, report, geo
    df, report = core.load_and_validate(io.BytesIO(file_bytes))
    df, geo = core.geocode_batch(df)
    m = core.engineer(df)
    gam, m, stats = core.fit(m)
    return gam, m, stats, report, geo


if up is not None and not use_demo:
    key, demo = up.getvalue(), False
elif use_demo:
    key, demo = None, True
else:
    st.info("Upload your MLS closed-sales CSV to begin (see README for the columns it expects).")
    st.stop()

with st.spinner("Running the pipeline — geocoding + model fit takes ~1-2 minutes on a fresh file..."):
    try:
        gam, m, stats, report, geo = run_pipeline(key, demo)
    except ValueError as e:
        st.error(str(e))
        st.stop()

# ---------- header metrics ----------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Sales in model", f"{stats['n']:,}")
c2.metric("Model R²", f"{stats['r2']:.2f}")
c3.metric("Typical error", f"{stats['med_pct_err']:.1f}%")
c4.metric("Geocoded", f"{geo['matched']}/{geo['total']}")
c5.metric("12-mo market change", f"{core.trailing_12mo_pct(gam, m):+.1f}%")
if stats["n"] < 300:
    st.warning("Under 300 sales — adjustments will have wide, soft ranges. Add more data if you can.")

tab_qa, tab_table, tab_trend, tab_map, tab_comps, tab_check = st.tabs(
    ["🎯 Ask the model", "📋 Full adjustment table", "📈 Market trend",
     "🗺️ Location map", "🏠 Comp finder", "🔍 Data check"])

# ---------- Ask the model (Q&A) ----------
with tab_qa:
    st.subheader("What is the adjustment for ... ?")
    choice = st.selectbox("Pick a feature", list(core.NICE.values()))
    col = [k for k, v in core.NICE.items() if v == choice][0]

    if col in core.SMOOTH_TERMS and col != "t_days":
        slope, lo, hi, a, b = core.smooth_slope_range(gam, m, col)
        unit = {"gla": "per sqft", "acreage": "per 0.1 acre", "year_built": "per year newer"}[col]
        mult = 0.1 if col == "acreage" else 1.0
        cA, cB = st.columns(2)
        cA.metric(f"Adjustment ({unit})", f"${slope*mult:,.0f}",
                  help=f"Slope measured across the middle of your data ({a:,.2f} to {b:,.2f})")
        cB.metric("Model 95% range", f"${lo*mult:,.0f} to ${hi*mult:,.0f}")
        grid, pdep, ci = core.smooth_curve(gam, core.SMOOTH_TERMS[col])
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(grid, pdep, color="#2c5aa0", lw=2.5)
        ax.fill_between(grid, ci[:, 0], ci[:, 1], alpha=0.18, color="#2c5aa0")
        lo_d, hi_d = m[col].quantile(0.02), m[col].quantile(0.98)
        ax.set_xlim(lo_d, hi_d)
        ax.set_xlabel(choice)
        ax.set_ylabel("Contribution to price ($)")
        ax.yaxis.set_major_formatter(lambda x, _: f"${x/1000:,.0f}k")
        ax.set_title(f"How {choice.lower()} contributes to price in YOUR market")
        st.pyplot(fig)
        st.caption("The curve is the model's full answer — adjustments aren't one flat number. "
                   "Steeper sections = the market pays more per unit there. Shaded band = 95% confidence.")
    elif col == "t_days":
        pct = core.trailing_12mo_pct(gam, m)
        st.metric("Constant-quality market change, trailing 12 months", f"{pct:+.1f}%")
        st.caption("See the Market trend tab for the full curve.")
    else:
        slope, lo, hi = core.linear_effect(gam, core.LINEAR_TERMS[col])
        cA, cB = st.columns(2)
        cA.metric("Adjustment (per unit)", f"${slope:,.0f}")
        cB.metric("Model 95% range", f"${lo:,.0f} to ${hi:,.0f}")
        share_zero = "crosses $0 — treat as a starting point, not gospel" if lo < 0 < hi else "does not cross $0 — direction is well supported"
        st.caption(f"The 95% range {share_zero}.")
        if col == "beds":
            st.info("A negative bedroom number is normal in market-derived models: holding GLA "
                    "constant, an extra bedroom means smaller rooms. The value lives in the "
                    "square footage, not the bedroom count.")

# ---------- full table ----------
with tab_table:
    rows = []
    for col2, ti in core.LINEAR_TERMS.items():
        sl, lo, hi = core.linear_effect(gam, ti)
        rows.append((core.NICE[col2], f"${sl:,.0f}", f"${lo:,.0f} to ${hi:,.0f}"))
    for col2 in ("gla", "acreage", "year_built"):
        sl, lo, hi, a, b = core.smooth_slope_range(gam, m, col2)
        mult = 0.1 if col2 == "acreage" else 1
        unit = {"gla": " ($/sqft)", "acreage": " ($/0.1 ac)", "year_built": " ($/yr)"}[col2]
        rows.append((core.NICE[col2] + unit, f"${sl*mult:,.0f}", f"${lo*mult:,.0f} to ${hi*mult:,.0f}"))
    st.dataframe(pd.DataFrame(rows, columns=["Feature", "Adjustment", "95% range"]),
                 use_container_width=True, hide_index=True)
    st.caption("Ranges are model confidence intervals; true uncertainty is somewhat wider. "
               "Wide range = thin support in your data, not necessarily a wrong number.")

# ---------- trend ----------
with tab_trend:
    grid, pdep, _ = core.smooth_curve(gam, 3)
    med = m["sold_price"].median()
    trend = med + (pdep - np.interp(m["t_days"].median(), grid, pdep))
    dates = m["sold_date"].min() + pd.to_timedelta(grid, unit="D")
    mm = m.set_index("sold_date").resample("ME")["sold_price"].median()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.scatter(m["sold_date"], m["sold_price"], s=12, alpha=0.3, color="#888", label="Sales")
    ax.plot(mm.index, mm.values, "o-", color="#b58500", lw=1, ms=3, label="Monthly median (raw)")
    ax.plot(dates, trend, color="#2c5aa0", lw=3, label="Constant-quality trend (GAM)")
    ax.set_ylim(0, m["sold_price"].quantile(0.99) * 1.15)
    ax.yaxis.set_major_formatter(lambda x, _: f"${x/1000:,.0f}k")
    ax.legend()
    st.pyplot(fig)
    st.metric("12-month constant-quality change", f"{core.trailing_12mo_pct(gam, m):+.1f}%")
    st.caption("The GAM line tracks the same-quality home over time; raw medians move with the "
               "mix of what sold. When they disagree, trust the blue line.")

# ---------- residual map ----------
with tab_map:
    g = m.dropna(subset=["lat", "lon"])
    cap = 75000
    fmap = folium.Map(location=[g.lat.mean(), g.lon.mean()], zoom_start=12,
                      tiles="cartodbpositron")
    def rcolor(v):
        x = max(0, min(1, (v + cap) / (2 * cap)))
        r = int(255 * min(1, 2 * x)); b = int(255 * min(1, 2 * (1 - x)))
        return f"#{r:02x}{int(80*(1-abs(2*x-1))):02x}{b:02x}"
    for _, row in g.iterrows():
        folium.CircleMarker([row.lat, row.lon], radius=5, color=None, fill=True,
                            fill_color=rcolor(np.clip(row.resid, -cap, cap)), fill_opacity=0.75,
                            tooltip=f"sold ${row.sold_price:,.0f} · model ${row.pred:,.0f} · {row.resid:+,.0f}"
                            ).add_to(fmap)
    components.html(fmap._repr_html_(), height=520)
    st.caption("🔴 sold above what features predict (location premium) · "
               "🔵 sold below (location discount). Clusters of one color = a real "
               "locational adjustment worth investigating.")

# ---------- comp finder ----------
with tab_comps:
    st.subheader("Find the best comps for your subject")
    with st.form("subject"):
        c1, c2, c3 = st.columns(3)
        addr = c1.text_input("Subject address (street, city, ST zip)")
        gla_v = c2.number_input("GLA (above-grade sqft)", 400, 12000, 2000)
        yr = c3.number_input("Year built", 1880, 2026, 2005)
        c4, c5, c6, c7 = st.columns(4)
        ac = c4.number_input("Lot (acres)", 0.01, 40.0, 0.25)
        bd = c5.number_input("Bedrooms", 1, 10, 3)
        fb = c6.number_input("Full baths", 1, 8, 2)
        hb = c7.number_input("Half baths", 0, 4, 0)
        c8, c9, c10, c11 = st.columns(4)
        bs = c8.number_input("Basement sqft", 0, 6000, 0)
        gs = c9.number_input("Garage spaces", 0, 6, 2)
        fp = c10.number_input("Fireplaces", 0, 5, 0)
        nc = c11.slider("How many comps", 3, 15, 10)
        mw = st.slider("How much does distance matter? ($ penalty per mile)",
                       0, 50000, 15000, step=5000)
        recent = st.checkbox("Only sales from the last 12 months", value=False)
        go = st.form_submit_button("Find comps")

    if go:
        lat = lon = None
        if addr.strip():
            lat, lon = core.geocode_one(addr)
            if lat is None:
                st.warning("Couldn't geocode that address — ranking on features only, no distance penalty.")
        subject = {"gla": gla_v, "acreage": ac, "year_built": yr, "beds": bd,
                   "full_baths": fb, "half_baths": hb, "bsmt": bs,
                   "garage_spaces": gs, "fireplaces": fp,
                   "lat": lat, "lon": lon}
        comps = core.rank_comps(gam, m, subject, n_comps=nc, miles_weight=mw,
                                max_age_days=365 if recent else None)
        show = comps[["Street #", "Street/Road Name", "Subdivision", "sold_date",
                      "sold_price", "time_adj_price", "gla", "year_built", "beds",
                      "full_baths", "acreage", "miles", "dollar_distance"]].copy()
        show.columns = ["St#", "Street", "Subdivision", "Sold", "Sold price",
                        "Time-adj price", "GLA", "Built", "Bd", "Ba", "Acres",
                        "Miles", "$ distance"]
        show["Sold"] = pd.to_datetime(show["Sold"]).dt.date
        for c in ("Sold price", "Time-adj price", "$ distance"):
            show[c] = show[c].map(lambda x: f"${x:,.0f}")
        show["Miles"] = show["Miles"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.metric("Indicated range (time-adjusted comp prices)",
                  f"${comps.time_adj_price.min():,.0f} — ${comps.time_adj_price.max():,.0f}",
                  help="Range of the selected comps' prices adjusted to today's market by the time curve. A starting point, not a value conclusion.")

        gg = comps.dropna(subset=["lat", "lon"])
        if len(gg) and lat:
            cmap = folium.Map(location=[lat, lon], zoom_start=13, tiles="cartodbpositron")
            folium.Marker([lat, lon], tooltip="SUBJECT",
                          icon=folium.Icon(color="red", icon="home", prefix="fa")).add_to(cmap)
            for rank, (_, row) in enumerate(gg.iterrows(), 1):
                folium.Marker([row.lat, row.lon],
                              tooltip=f"#{rank}: {row['Street #']} {row['Street/Road Name']} — ${row.sold_price:,.0f}",
                              icon=folium.DivIcon(html=f'<div style="background:#2c5aa0;color:white;'
                                   f'border-radius:50%;width:24px;height:24px;text-align:center;'
                                   f'line-height:24px;font-weight:bold">{rank}</div>')).add_to(cmap)
            components.html(cmap._repr_html_(), height=520)
        st.caption("Ranked by dollar-distance: the model's own adjustment curves convert every "
                   "feature difference into dollars, plus your distance penalty. "
                   "Time-adj price = sold price brought to today using the market curve.")

# ---------- data check ----------
with tab_check:
    st.write(f"**Rows:** {report['rows']}  ·  **Dates:** {report['date_min']} → {report['date_max']}"
             f"  ·  **Median price:** ${report['median_price']:,.0f}")
    if report["issues"]:
        for i in report["issues"]:
            st.warning(i)
    else:
        st.success("No blocking data issues found.")
    if report["missing"]:
        st.write("**Blank values by column:**")
        st.dataframe(pd.DataFrame(list(report["missing"].items()),
                                  columns=["Column", "Blank rows"]),
                     hide_index=True)
    st.markdown("---")
    st.markdown(
        "**Known limitations** — concessions Yes/No only (prices not cash-equivalent "
        "adjusted); no quality/condition ratings (their value bleeds into location and "
        "year-built); no arm's-length screening; no cost-approach data (needs a licensed "
        "cost service). Every number here is a market-derived *starting point* for your "
        "analysis — you are the appraiser.")
