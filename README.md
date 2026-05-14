# AI Appraiser Tools

Free, open-source tools for real estate appraisers, built by [The Appraiser Coach](https://www.theappraisercoach.com).

Every tool runs entirely in the browser — no signup, no data leaves the user's computer, no subscription required.

## Tools

| Tool | What it does |
|---|---|
| [Depreciated Cost Calculator](./depreciated-cost-calculator/) | Drop in an appraisal PDF, get suggested adjustment ranges for GLA, basement, and garage derived from the report's own Cost Approach. |
| [133-Step QC Reviewer (prompt template)](./qc-reviewer/) | Pre-submission QC checklist. Copy the prompt into Claude.ai or ChatGPT, attach your appraisal PDF, get severity-rated concerns with step references. Requires a paid AI subscription. |

## Using the tools

Visit the live site:

**https://theappraisercoach.github.io/ai-appraiser-tools/**

Each tool has its own page — drop in a PDF, get adjustments, copy the suggested narrative.

## For developers

Every tool is a single self-contained HTML file. No build step, no framework, no server. Just open the file in any browser and it works.

To run locally:

```
git clone https://github.com/TheAppraiserCoach/ai-appraiser-tools.git
cd ai-appraiser-tools
python3 -m http.server 8000
# open http://localhost:8000
```

## Contributing

Issues and pull requests welcome. If you're an appraiser with an idea for a tool, open an issue and describe what it should do.

## License

MIT. Use them, fork them, modify them, ship your own version. Attribution appreciated but not required.

## More from The Appraiser Coach

Coaching, training, community, and the bigger workflows are at [theappraisercoach.com](https://www.theappraisercoach.com).
