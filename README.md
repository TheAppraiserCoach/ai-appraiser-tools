# AI Appraiser Tools

Free, open-source tools for real estate appraisers, built by [The Appraiser Coach](https://www.theappraisercoach.com ).

Every tool runs entirely in the browser — no signup, no data leaves the user's computer, no subscription required.

## Tools

| Tool | What it does |
|---|---|
| [Depreciated Cost Calculator](./depreciated-cost-calculator/) | Drop in an appraisal PDF, get suggested adjustment ranges for GLA, basement, and garage derived from the report's own Cost Approach. |
| [133-Step QC Reviewer (prompt template)](./qc-reviewer/) | Pre-submission QC checklist. Copy the prompt into Claude.ai or ChatGPT, attach your appraisal PDF, get severity-rated concerns with step references. Requires a paid AI subscription. |
| [Revision Response Writer (prompt template)](./revision-writer/) | Drafts addendum-ready responses to AMC / underwriter revision requests. Categorizes each item (already addressed / correction / clarification / misunderstanding / out-of-scope) and writes in appraiser voice with appropriate standards citations. Requires a paid AI subscription. |
| [Engagement Letter Parser (prompt template)](./engagement-letter-parser/) | Drop in an engagement letter PDF, get all the order-setup fields in a clean structured format (property, borrower, lender, AMC, fee, due date, loan type, contacts, case numbers, legal description, special instructions). Saves 5–10 minutes of typing per order. Requires a paid AI subscription. |
| [Photo Quality Checker (prompt template, vision-required)](./photo-quality-checker/) | Drop in a completed report PDF. The AI reviews every photo and flags missing required angles, missing interior coverage (with FHA/VA escalation), condition-rating mismatches, quality-rating consistency, and photo-quality issues (blurry, dark, obstructed, watermarked stock). Severity-rated output. Requires a paid AI subscription with a vision-capable model. |
| [Neighborhood Narrative Builder (prompt template)](./neighborhood-narrative-builder/) | Give it the subject address + the four neighborhood-character trend boxes, get suggested N/S/E/W major-road boundaries plus the Neighborhood Description and Market Conditions narratives. Third-person report voice. Marks placeholders for any specific data not provided. Requires a paid AI subscription. |
| [Reconciliation Narrative Writer (prompt template, vision-required)](./reconciliation-narrative-writer/) | Drop in a completed report PDF or grid screenshot. Reads the adjusted grid, classifies each comp (closed / pending / active), suggests reconciliation weights summing to 100% across closed sales only, and drafts the three-paragraph reconciliation narrative. Requires a paid AI subscription with a vision-capable model. |
| [Interactive Appraisal Report](./interactive-appraisal-report/) | A password-protected, interactive website that replaces the static PDF for private appraisal clients. Includes 15 clickable sections — value summary, neighborhood map, market analysis charts, sales comparison grid, cost approach visualization, photo gallery, building sketch, FAQ, and more. Hosted for 90 days with a built-in Save PDF button. Branded to the appraiser.  |
| [Comp Verification (prompt template)](./comp-verification/) | Drafts verification emails to listing agents — one per agent, combining their comps. Asks about concessions, buyer-agent compensation, multiple offers, related parties, and close price/date confirmation. Paste your comps into Claude.ai or ChatGPT, get ready-to-send emails. Requires a paid AI subscription. |
| [AI Voice Agent Builder (prompt template)](./voice-agent-builder/) | Walks you through building a phone agent that answers calls when you cannot, on the platform of your choice. Includes a build-coach prompt and a ready-to-edit agent script. Bring your own AI chat. |

## Using the tools

Visit the live site:

**https://theappraisercoach.github.io/ai-appraiser-tools/**

Each tool has its own page — drop in a PDF, get adjustments, copy the suggested narrative.

## For developers

Every tool is a single self-contained HTML file. No build step, no framework, no server. Just open the file in any browser and it works.

To run locally:

