# AI Appraiser Tools

Free AI tools for residential appraisers, from [The Appraiser Coach](https://www.theappraisercoach.com).

---

## 👉 Start here: [OPEN THE TOOLS](https://theappraisercoach.github.io/ai-appraiser-tools/)

**Click the link above.** That's it. Every tool opens as a normal web page with a big button. No download, no signup, nothing to install.

You do NOT need a GitHub account. You do NOT need to understand the list of folders above this page.

---

## Wait, what is this page?

GitHub is where software people store and share files. Think of this page as the **storage room**. The folders at the top of the screen are the raw files behind each tool.

The **showroom** is the link above. Same tools, but they open like a regular website.

> **Clicked a folder and saw a wall of code?** That's normal. You opened the raw file in the storage room. Come back here and use the **OPEN THE TOOLS** link instead.

---

## How most of these tools work (3 minutes, one time)

Most tools here are **prompt templates**. A prompt is a set of instructions you hand to an AI. We wrote the instructions. You bring the AI and your report.

1. Click **[OPEN THE TOOLS](https://theappraisercoach.github.io/ai-appraiser-tools/)** and pick a tool.
2. Click the **📋 Copy prompt** button on that tool's page.
3. In another tab, open **[Claude.ai](https://claude.ai)** or **[ChatGPT](https://chatgpt.com)** and start a **new chat**.
4. **Paste** the prompt into the message box. Don't hit send yet.
5. **Attach** your file (paperclip icon). Usually your appraisal PDF.
6. **Send.** Give it 30 to 90 seconds.
7. **Read it like a reviewer, not a robot.** You are still the appraiser. Check it, fix it, then paste into TOTAL.

**What you need:** a paid AI plan (Claude Pro or ChatGPT Plus, about $20/month). The free versions usually can't read PDFs or photos well enough.

**Tip:** keep that chat open. Ask follow-ups like *"show me the math on concern #3."*

---

## Which tool do I use?

| When you need to | Use this | Type |
|---|---|---|
| Catch problems before you submit | [133-Step QC Reviewer](https://theappraisercoach.github.io/ai-appraiser-tools/qc-reviewer/) | Prompt |
| Check your photos against your ratings | [Photo Quality Checker](https://theappraisercoach.github.io/ai-appraiser-tools/photo-quality-checker/) | Prompt |
| Answer an AMC or underwriter revision | [Revision Response Writer](https://theappraisercoach.github.io/ai-appraiser-tools/revision-writer/) | Prompt |
| Set up a new order fast | [Engagement Letter Parser](https://theappraisercoach.github.io/ai-appraiser-tools/engagement-letter-parser/) | Prompt |
| Write the neighborhood section | [Neighborhood Narrative Builder](https://theappraisercoach.github.io/ai-appraiser-tools/neighborhood-narrative-builder/) | Prompt |
| Write the reconciliation | [Reconciliation Narrative Writer](https://theappraisercoach.github.io/ai-appraiser-tools/reconciliation-narrative-writer/) | Prompt |
| Email agents to verify comps | [Comp Verification](https://theappraisercoach.github.io/ai-appraiser-tools/comp-verification/) | Prompt |
| Support GLA, basement, garage adjustments | [Depreciated Cost Calculator](https://theappraisercoach.github.io/ai-appraiser-tools/depreciated-cost-calculator/) | Works on the page, no AI needed |
| Have an AI answer your phone | [AI Voice Agent Builder](https://theappraisercoach.github.io/ai-appraiser-tools/voice-agent-builder/) | Prompt + guide |
| Onboard a new trainee or contractor | [Onboarding Kit](https://theappraisercoach.github.io/ai-appraiser-tools/appraiser-onboarding-kit/) | Download (advanced) |
| Give your AI a memory of you and your business | [Personal OS Starter](./personal-os-starter/) | Download |
| Deliver a private report as a website | [Interactive Appraisal Report](./interactive-appraisal-report/) | Developer project (advanced) |
| Read how we had AI read and write TOTAL files | [Automating TOTAL white paper](https://theappraisercoach.github.io/ai-appraiser-tools/total-automation-whitepaper/) | Read only |

**New to all this? Start with the QC Reviewer.** It's the fastest "aha" in the bunch.

---

## The download tools (only if you need them)

A few items are folders of files, not web pages. To grab them:

1. Scroll to the top of this page.
2. Click the green **`<> Code`** button.
3. Click **Download ZIP**.
4. Unzip it on your computer and open the folder for the tool you want. Each one has its own README with setup steps.

---

## Common questions

**"I tried to download the reviewer and it didn't work."**
You don't download it. Open the [QC Reviewer page](https://theappraisercoach.github.io/ai-appraiser-tools/qc-reviewer/), click **Copy prompt**, and paste it into Claude or ChatGPT.

**"Do I need a GitHub account?"**
No. Only if you want to save your own copy or suggest changes.

**"Is my report data sent to you?"**
No. The pages run in your browser. When you use a prompt, your PDF goes to whichever AI you choose (Claude or ChatGPT), under your own account.

**"The AI said it can't read my PDF."**
You're probably on a free plan or an older model. Switch to a paid plan and pick the top model.

**"Can I change the prompt?"**
Yes. Paste it into your AI, then tell it what to change. It's yours.

**"Something is broken."**
Let us know in the member community or at [theappraisercoach.com](https://www.theappraisercoach.com).

---

<details>
<summary><b>For the tech-curious (skip this)</b></summary>

Every browser tool is a single self-contained HTML file. No build step, no framework, no server. Download the file, double-click it, and it opens in your browser.

The site above is published with GitHub Pages from the `main` branch. Fork the repo, change what you want, and turn on Pages in your fork to host your own copy.

Licensed MIT. See [LICENSE](./LICENSE).
</details>
