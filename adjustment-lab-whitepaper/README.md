# Adjustment Lab: Market-Derived Adjustments From Your Own MLS Export — A Dustin OS White Paper

> **Read the designed version:** https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/  
> **PDF:** https://theappraisercoach.github.io/ai-appraiser-tools/dist/Adjustment-Lab-Whitepaper.pdf  
> This README is the same paper in plain Markdown so it reads here on GitHub.

Published by The Appraiser Coach, October 2026. The tool is live at [adjust.dustinharrisos.com](https://adjust.dustinharrisos.com/) (password `appraiser2026`) and its source is in [this repository](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab/). Built July 2026 for a hands-on workshop; published now because people keep asking.

> ### Read this first
>
> - **This is an exploratory tool, not a valuation.** Nothing it produces is a substitute for appraiser judgment, and nothing here is USPAP guidance. Every adjustment it reports should be treated as a starting point to test, not a number to transcribe.
> - **The model only knows what the MLS export tells it.** Section 6 lists what it cannot see. Read that section before you use a single figure.
> - **No warranty, no tech support.** Source is published so you can check it, run it, and improve it.

> ### Contents
>
> 1. [The problem: "support" that isn't](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#why)
> 2. [What the tool does, in one walk-through](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#what)
> 3. [The model, in plain English](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#model)
> 4. [The seven steps under the hood](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#pipeline)
> 5. [What the Idaho Falls numbers actually said](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#numbers)
> 6. [What it cannot see (the honest section)](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#limits)
> 7. [How it was built](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#built)
> 8. [How to use it without getting burned](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#use)
> 9. [If you want to run it on your market](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab-whitepaper/#tryit)

## 1. The problem: "support" that isn't

Ask ten appraisers where their garage adjustment comes from and you will get ten versions of the same answer: it's what we've always used, it's what the market seems to bear, it's somewhere between paired sales from six years ago and a number a reviewer didn't push back on. Under UAD 3.6 and the current reviewer climate, that is not going to hold. Lenders are asking for support, and "experience" is not a column in a spreadsheet.

There are commercial services that will derive adjustments from your market's sales for a monthly fee. They work. They are also a black box, they cost money every month whether you use them or not, and your data goes to them. The question this project set out to answer was narrow: **can an appraiser with no statistics background, using an AI assistant, build the same kind of analysis on his own machine, from his own MLS export, with the math visible?**

The answer turned out to be yes, in about a weekend, and the result is good enough to use carefully and not good enough to use blindly. This paper is about the difference.

## 2. What the tool does, in one walk-through

You export closed sales from your MLS as a CSV. For the test, that was 845 sales in Idaho Falls, Idaho, from July 2024 to July 2026. You upload the file. The tool validates it, geocodes the addresses through the US Census Bureau's free geocoder, fits a model, and about ninety seconds later gives you six tabs:

- **Ask the model.** Pick a feature, get the dollar adjustment, the 95% range, and a curve showing how the contribution changes across the feature's range (a third bathroom is not worth the same as a second one).
- **Full table.** Every feature's adjustment and range on one page, ready to screenshot into a workfile.
- **Market trend.** A constant-quality price index for your market over the period, which is the time adjustment, computed the way an economist would compute it rather than from raw monthly medians.
- **Residual map.** Once size, age, and features are stripped out, which neighborhoods are selling above or below what the model expects. That is your location adjustment, drawn as a heat map.
- **Comp finder.** Enter a subject's specs and address. The tool uses its own curves to convert every candidate sale's feature differences into dollars, adds a distance penalty you control with a slider, time-adjusts each price, and ranks the comps by how little adjustment they need. The best comp is the one that needs the least fixing, not the one that happens to be closest.
- **Data check.** What the export was missing, what got excluded, and how many addresses would not geocode.

## 3. The model, in plain English

The statistical engine is a *generalized additive model*, a GAM. Here is the whole idea without the vocabulary.

A plain regression says: price equals a fixed dollar amount per square foot, plus a fixed amount per bathroom, plus a fixed amount per year of age, and so on, every feature a straight line. Appraisers know that is false. The first 500 square feet of living area is worth more per foot than the last 500. A house built in 1950 versus 1960 is not the same gap as 2010 versus 2020. Straight lines force the model to split the difference and get every point a little wrong.

A GAM lets each feature have its own *curve* instead of a line. The curve is learned from the data, and the model is told not to let any curve wiggle more than the sales justify. Living area, lot size, year built, and sale date get curves. Beds, baths, basement, garage spaces, fireplaces, patio/deck, central air, HOA, and view are counted or yes/no, so they get straight contributions. Garage type (none, attached, detached, carport) is treated as categories. Add every contribution together and you get a predicted price; the difference between predicted and actual is the *residual*, which is where location lives.

Two things make this more honest than a spreadsheet of paired sales:

- **Every adjustment is estimated with every other feature held constant.** The bathroom adjustment is what a bathroom is worth when size, age, lot, and date are the same. That is what an adjustment is supposed to mean, and it is nearly impossible to get from hand-picked pairs.
- **Every adjustment comes with a range.** The 95% range is the model's own statement of how sure it is. A tight range means the market spoke clearly. A range that crosses zero means the market did not, and you should not pretend otherwise in a grid.

The sale-date curve is the time adjustment. Because the model has already accounted for what sold (size, age, features), the date curve measures what the *same house* would have sold for over time, a constant-quality index. Raw monthly medians cannot do this; if smaller homes happen to sell one month, the median drops and it looks like the market fell.

## 4. The seven steps under the hood

| Step | What it does | Why it matters |
|---|---|---|
| 1 Validate | Loads the CSV, checks required columns, parses dates and numbers, flags blanks and impossible values. | On the test data it caught one listing with all its square footage logged below grade and repaired it. Garbage in is the main way these models lie. |
| 2 Geocode | Sends street addresses (no prices) to the US Census geocoder; 94% matched. | No coordinates, no map. Unmatched sales stay in the model but off the map, never faked. |
| 3 Fit | Fits the GAM; refits with monotonic living-area so the curve cannot bend downward. | R² of 0.88 and a 5-fold cross-validated error of 9.3% versus 8.9% in-sample, so it is not memorizing the data. |
| 4 Adjustments | Reads each contribution off its curve at typical values; reports the dollar figure and the 95% range. | This is the table in section 5. |
| 5 Bootstrap | Refits the model 200 times on resampled data for one adjustment (fireplace) to see how wide the honest range really is. | The model's own range for fireplace was tighter than the bootstrap's. Lesson: the formal ranges are optimistic; the bootstrap is truth. |
| 6 Trend | Plots the constant-quality index against raw monthly medians. | Shows the mix effect in your own market. |
| 7 Map | Plots residuals by location; summarizes by subdivision. | Location premiums and discounts with sale counts, so you know which ones are solid. |

The web app wraps steps 1 through 4 and 6 and 7 behind an upload button and adds the comp finder. The command-line scripts are published separately so anyone can read exactly what was done.

## 5. What the Idaho Falls numbers actually said

Rounded, from 845 sales, July 2024 to July 2026. Published to show the shape of the output, not as adjustments for your market.

| Feature | Adjustment | 95% range | Read |
|---|---|---|---|
| Market, trailing 12 months | +3.4% constant-quality | — | Modest, healthy. Raw medians looked flatter; that gap was mix. |
| Full bath | $21,400 | $11,000–$31,900 | Well supported. |
| Half bath | $24,600 | $12,300–$36,800 | Well supported (and yes, higher than a full bath in this sample; small-sample quirk, note it). |
| Basement, per sq ft below grade | $60 | $48–$72 | Tight. Defensible. |
| Garage space, each | $13,600 | $4,400–$22,700 | Supported; the count carries the value, the type adds little. |
| Central air | $25,300 | $14,200–$36,400 | Supported. |
| Year built, per year newer | $868 | $811–$926 | Tight, but see section 6: this is absorbing condition. |
| Lot, per 0.1 acre (0.15–0.29 ac) | $18,750 | — | Strong in this band only. |
| Fireplace, each | $6,500 (bootstrap median) | $2,300–$12,500 | Fuzzy. A starting point. |
| Patio/deck, each | $4,300 | −$1,900–$10,600 | Range crosses zero. The market did not speak. |
| Bedroom, each, GLA held constant | −$5,900 | −$12,000–$100 | Not an error; see below. |
| View noted in MLS | $34,900 | $14,500–$55,300 | Real but measured off 56 flagged sales; the field is 93% blank. |

> **The bedroom line is the most useful thing in the table.** Holding square footage constant, an extra bedroom came out slightly negative, because at the same size, more bedrooms means smaller rooms. Bedrooms do not carry value; the square footage they occupy does. Every hedonic model behaves this way. If your grid adjusts for both GLA and bedroom count, you are double-counting, and this is the data telling you so.

On the map, after features were stripped out, three subdivisions showed consistent premiums and three showed consistent discounts, with sale counts attached. The one with 62 sales was statistically solid; the one with the biggest premium was partly true location and partly custom-home quality the data cannot see, which is the segue to the next section.

## 6. What it cannot see (the honest section)

1. **No quality or condition ratings.** The two biggest absences in a typical export. Their value bleeds into year built, living area, and especially the location residuals. A "premium neighborhood" on the map is partly a "well-kept houses" neighborhood.
2. **Concessions are Yes/No, not dollars.** 57% of the sample had concessions of unknown size. Sold prices are not cash-equivalent. If typical concessions run $5,000 to $10,000, every adjustment carries that fog.
3. **No arm's-length screening.** No REO, estate, or relocation flags in the export, so distressed sales are in the sample unmarked.
4. **The formal ranges are optimistic.** The bootstrap on fireplace proved it. Treat the published 95% ranges as the narrow end of the truth.
5. **About 6% of addresses would not geocode.** They are in the model, off the map.
6. **No cost approach.** Replacement cost needs licensed cost data; it is not derivable from sales.
7. **Sample size was not the limit; column coverage was.** 845 sales is plenty. The missing fields are what hurt.

None of these are flaws in the method. They are flaws in what an MLS export contains, and they would affect a commercial service exactly the same way, except that a commercial service may not tell you.

## 7. How it was built

The person who built this is an appraiser of thirty years with no statistics training and no ability to write code. The AI assistant did the statistics and the code. The appraiser did three things, and they were the three things that mattered:

1. **Described the problem in appraisal terms.** "I want adjustments with ranges from my own sales, a time adjustment that isn't fooled by mix, and a map of where location is doing the work." The assistant chose the GAM; the appraiser never had to.
2. **Read every number and argued with it.** The negative bedroom adjustment got pushed back on and turned out to be right. The half-bath-above-full-bath result got flagged as a quirk to note. The fireplace range looked too clean and the bootstrap step exists because of that question.
3. **Insisted on the limitations section.** The first draft of the report did not have one. The appraiser's instinct that "this is going in front of a reviewer someday" is what produced section 6.

Timeline: the seven-step analysis and the report were a Saturday. The web app wrapping it was a Sunday. Deployment on a small home server behind a password took an evening, most of it fighting a tunnel configuration quirk that is now written down in the repository so nobody has to fight it twice. It was shown at a workshop in July 2026 and has been sitting at its URL since.

The honest caveat about the build: the assistant that did it was running on a frontier model with a Python environment. It is not a prompt you paste into a chat window; the model has to be able to run code, see the output, and iterate. That capability is now a monthly subscription, not a research lab.

## 8. How to use it without getting burned

- **Use the ranges, not the point estimates.** If the range crosses zero, the honest adjustment is "not supported by this data," and that is a legitimate thing to write.
- **Reconcile against something.** Paired sales, cost, your own experience. When the model and the pairs agree, you have support. When they do not, you have a question worth answering in the workfile.
- **Say what the model could not see.** One sentence in the addendum: adjustments were developed from a regression on N local sales and reconciled with paired-sales analysis; the regression does not account for condition or concession amounts. Reviewers respect that more than false precision.
- **Re-run it quarterly.** It takes two minutes. The time adjustment in particular should not be last year's.
- **Never put the data anywhere.** Your MLS license is yours. The tool runs on your machine for a reason.

## 9. If you want to run it on your market

Everything is in the [adjustment-lab folder](https://theappraisercoach.github.io/ai-appraiser-tools/adjustment-lab/) of this repository: the app, the seven scripts, the example report, and a README with the exact CSV columns it expects and the commands to run it. Two hundred or more sales from one market over 18 to 24 months is the floor; 500 or more is where the ranges get useful.

If you would rather see it working before you install anything, the live demo at [adjust.dustinharrisos.com](https://adjust.dustinharrisos.com/) (password `appraiser2026`) will take your CSV. It is a small server and it is demo-grade; if it is slow, that is why.

> ### Repeat of the disclaimer
>
> - Exploratory tool. Not a valuation, not USPAP guidance, not a substitute for appraiser judgment.
> - Figures shown are from one market and one time period, rounded, for illustration only.
> - No warranty, no tech support. You are responsible for your MLS data license and for everything you put in a report.

---

*Published by [The Appraiser Coach](https://www.theappraisercoach.com). For the step-by-step version with your own market: the [Appraiser AI Academy](https://theappraisercoach.com/products/). Educational reference. No warranty, no tech support. Source on [GitHub](https://github.com/TheAppraiserCoach/ai-appraiser-tools).*
