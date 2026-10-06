# Idaho Falls Market Analysis — GAM Feature Adjustments
**Fable 5 / TrueTracts analytical test · 845 closed sales · Jul 2024 – Jul 2026**
*Exploratory tool for internal use. Not a substitute for appraiser judgment or USPAP sign-off.*

---

## What was run
1. Loaded and validated 845 closed sales (zero rows dropped; core fields 100% complete).
2. Geocoded 792/845 addresses (93.7%) via the US Census bulk geocoder — no fabricated coordinates; 53 unmatched sales stay in the model but off the map.
3. Fit a GAM: smooth terms for GLA (monotonic), lot size, year built, and sale date (the time/market term); linear terms for beds, baths, basement sqft, garage, fireplace, patio/deck, AC, HOA, view; categorical garage type.
4. Extracted marginal dollar adjustments with confidence ranges.
5. Bootstrapped the fireplace adjustment (200 refits).
6. Built the market trend chart.
7. Built the spatial residual map (interactive HTML + PNG).

**Model quality: R² 0.879 · median error 8.9% · 5-fold cross-validated error 9.3%** (in-sample ≈ out-of-sample, so it is not overfitting). One data repair: MLS 2167867 had all sqft logged below grade; main-floor 1,844 sqft restored as GLA.

## Adjustment table (95% ranges)

| Feature | Adjustment | 95% range |
|---|---|---|
| GLA, marginal $/sqft (1,000–1,850 band) | $31 | wider in truth — see note |
| GLA, average $/sqft across full range | ~$93 | — |
| Lot size, per 0.1 acre (0.15–0.29 ac band) | $18,750 | — |
| Year built, per year newer (1950–1996) | $868 | $811–$926 |
| Market conditions, trailing 12 mo | **+3.4% constant-quality** | — |
| Bedroom (each, GLA held constant) | −$5,900 | −$12,000–$100 |
| Full bath | $21,400 | $11,000–$31,900 |
| Half bath | $24,600 | $12,300–$36,800 |
| Basement, $/sqft below grade | $60 | $48–$72 |
| Garage space (each) | $13,600 | $4,400–$22,700 |
| Fireplace (each) | $6,500 (bootstrap median) | P10 $2,300 – P90 $12,500 |
| Patio/deck feature (each) | $4,300 | −$1,900–$10,600 |
| Central air | $25,300 | $14,200–$36,400 |
| View noted in MLS | $34,900 | $14,500–$55,300 |
| Garage: Detached vs None | $17,900 | $4,200–$31,700 |
| Garage: Attached vs None | $700 | −$11,000–$12,400 |

## Plain-English read (the narrative)

**What's driving value in this dataset:** size and land, overwhelmingly. GLA and lot size together do most of the work, with the market itself adding a steady +3.4% constant-quality over the last 12 months — modest, healthy appreciation, not a hot market. Raw monthly medians look flatter than that; the difference is mix (more modest homes selling lately), which is exactly why a time-adjusted model beats eyeballing medians.

**Well-supported adjustments** (tight ranges, believable magnitudes): basement $/sqft, full and half baths, garage spaces, central air, lot size, the time trend. These you could defend from this data.

**The bedroom line is not a mistake.** Holding square footage constant, an extra bedroom shows as slightly negative — because at the same GLA, more bedrooms means smaller rooms. Bedrooms don't carry value; the square footage they occupy does. This matches how hedonic models always behave and is a good reminder not to double-count beds and GLA in a grid.

**Thin or fuzzy adjustments** (wide bands — treat as starting points, not gospel): fireplace ($2k–$12k honest range, median $6.5k), patio/deck count, HOA, carport, and the attached-vs-none garage *type* split (the spaces count carries the garage value; type adds little on top). The "view" premium ($35k) is real but the MLS field is 93% blank, so it's measured off only 56 flagged sales.

**Location signal (the map):** after stripping out features, consistent premiums show in Sand Pointe (+$173k median — likely part true location, part custom-home quality the data can't see), Yorkside (+$52k), and Bel Aire (+$28k over 62 sales, the most statistically solid). Consistent discounts: Holiday Hills (−$65k), Bristol Heights (−$40k), Summerfield (−$39k). Concentrated color on the map = a locational adjustment worth investigating, which is precisely the TrueTracts heat-map concept.

## Limitations — read this section closely
1. **No quality or condition ratings in the export.** The two biggest absences. Their value bleeds into year-built, GLA, and *especially* the location residuals. Sand Pointe's premium is partly this.
2. **Concessions are Yes/No, not dollars.** 57% of sales had concessions of unknown size; sold prices are NOT cash-equivalent adjusted. If typical concessions run ~$5–10k, every adjustment here carries that fog.
3. **No arm's-length screening.** The export has no REO/estate/relocation flags, so any distressed sales are in the sample unmarked.
4. **Marginal GLA CI is understated** ($31–32 is the model flattering itself); bootstrap-honest bands would be meaningfully wider, as the fireplace exercise shows.
5. **53 sales (6.3%) not geocodable** — in the model, off the map.
6. **No cost-approach capability.** Replacement-cost $/sqft requires licensed cost data (Marshall & Swift-type); not derivable from MLS sales. Feed manually if needed.
7. **Sample: 845 sales** — comfortably above the 750 ideal. Sample size is NOT a limitation here; column coverage is.

## Rerunning on a future CSV
Folder: `output/truetracts-test/`. Order: `step1_validate.py → step2_geocode.py → step3_gam.py → step3b_gam_refit.py → step4_adjustments.py → step5_bootstrap.py → step6_trend.py → step7_map.py` (venv: `.venv/bin/python`). Point step 1 at the new file (same column layout), everything downstream reruns unchanged.
