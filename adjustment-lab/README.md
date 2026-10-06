# Adjustment Lab

A web app that reads your MLS closed-sales export, fits a statistical model, and hands back **dollar adjustments with honest ranges** for GLA, lot size, year built, baths, garage, basement, fireplace, central air, view, and the market trend — plus a residual map that shows where location is adding or subtracting value, and a comp finder that ranks comparables in dollars, not miles.

**Try the live demo:** https://adjust.dustinharrisos.com — password **`appraiser2026`**
(demo-grade, running on one small server; it loads an 845-sale Idaho Falls dataset or your own CSV)

**Read how it was built:** [the white paper](../adjustment-lab-whitepaper/) — the method, what the numbers mean, and the limitations you must read before you put any of this in a report.

## What's in this folder

- `app/app.py`, `app/core.py` — the Streamlit app. Upload → validate → geocode (US Census, free) → fit → six tabs.
- `analysis/step1_validate.py … step7_map.py` — the original seven-step pipeline, runnable from the command line on your own CSV.
- `analysis/EXAMPLE-REPORT.md` — the full write-up the pipeline produced on the Idaho Falls sample, including the adjustment table and the limitations section.
- `requirements.txt` — Python packages, pinned.

**Not included:** the Idaho Falls sales data. MLS data is licensed to the member who exported it; publish code, never data.

## Run it on your own computer

```
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd app
APP_PASSWORD=yourpassword streamlit run app.py
```

Open the address Streamlit prints (usually http://localhost:8501), enter the password, upload your CSV.

To run the seven-step pipeline instead: `cd analysis && python step1_validate.py your_export.csv`, then steps 2–7 in order. Each step writes a small file the next one reads.

## The CSV it expects

A closed-sales export with these column headers (this is a standard Idaho/Flexmls export layout; rename yours to match if needed):

`MLS Number, Street #, Street/Road Name, City, State, Zip Code, Subdivision, Sold Date (MM/DD/YYYY), Sold Price, List Price, Original List Price, Days on Market, Seller Conc, Bedrooms, Bathrooms, Total Half Baths, Apx Acreage, Apx Year Built, Apx Total SqFt, Abv Grade SqFt, Blw Grade SqFt, Basement SqFt`

plus whatever garage, fireplace, patio/deck, AC, HOA, and view fields your MLS exports. 500+ sales from one market over 18–24 months is the sweet spot; under ~300 the ranges get wide.

## Privacy

Your data stays on the machine running the app. The only outside call is to the US Census Bureau's free geocoder, which receives street addresses (no prices) to turn them into map coordinates.

## Read this before you use a number

This is an exploratory tool, not a substitute for appraiser judgment or USPAP support. The model cannot see quality or condition ratings, cannot dollarize concessions when the MLS only records Yes/No, and does not screen for non-arm's-length sales. The white paper's limitations section says exactly how that affects each adjustment. Use the output as a starting point and a sanity check, and say so in your workfile.

No warranty, no tech support. Built with Claude Code by an appraiser, not a statistician; fork it and make it better.
