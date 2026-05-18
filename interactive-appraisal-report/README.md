# Interactive Appraisal Report

> A modern, password-protected, interactive web-based appraisal report — built as a premium alternative to static PDF delivery.

![React](https://img.shields.io/badge/React-19-blue?logo=react) ![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?logo=typescript) ![Tailwind](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss) ![License](https://img.shields.io/badge/License-MIT-green)

---

## What Is This?

Instead of delivering a static PDF appraisal report to your private clients, this tool gives them a **hosted, interactive website** that they can explore at their own pace. It is designed for certified residential appraisers who want to differentiate their service and deliver a premium client experience.

The report is **password-protected** (no account required — just a single shared password), expires automatically after a configurable number of days, and includes a **Save PDF** button so clients can keep a permanent copy.

---

## Live Demo

A working demo is available at the link below. Use the password `PEAK2026` to access it.

> **Demo:** [https://peakappraisal-f5bctq69.manus.space](https://peakappraisal-f5bctq69.manus.space)

---

## Features

| Feature | Description |
|---|---|
| **Password Gate** | Single-password protection with branded login screen. No accounts needed. |
| **15 Interactive Sections** | Full report navigation via a persistent left-rail sidebar |
| **Google Maps Integration** | Subject property pin + all comparable sales plotted on an interactive map |
| **Market Analysis Charts** | Median price trend, days on market, and price distribution (Recharts) |
| **Sales Comparison Grid** | All comparables with full adjustments table, expandable rows |
| **Cost Approach Visualization** | Horizontal bar chart breaking down replacement cost, depreciation, and land value |
| **Photo Gallery** | Category-filtered photo gallery with full-screen lightbox |
| **Building Sketch** | SVG floor plan with room labels, dimension lines, and area calculations table |
| **FAQ Accordion** | 10 pre-written client questions with appraiser-written answers |
| **Engagement & Payment** | Order letter timeline, payment confirmation, and intended use notice |
| **Save PDF Button** | Triggers browser print dialog with clean, professional print styles |
| **90-Day Expiration** | Countdown visible on cover; configurable expiration date |
| **Fully Brandable** | Swap in any appraiser's logo, colors, name, and license number |
| **Responsive Design** | Works on desktop, tablet, and mobile |

---

## Report Sections

1. Value Summary (Cover)
2. Engagement & Order
3. Payment Confirmation
4. Subject Property
5. Neighborhood
6. Site & GIS
7. Market Analysis
8. Sales Comparison
9. Cost Approach
10. Reconciliation
11. Narrative & Addenda
12. Photo Gallery
13. Building Sketch
14. Frequently Asked Questions
15. Appraiser Profile

---

## Tech Stack

- **React 19** + **TypeScript** — component-based UI
- **Tailwind CSS 4** — utility-first styling
- **shadcn/ui** — accessible UI primitives
- **Recharts** — market analysis charts
- **Google Maps JavaScript API** — neighborhood and comparable map (via Manus proxy — see note below)
- **Framer Motion** — section entrance animations
- **Wouter** — client-side routing
- **Vite** — build tooling

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) v18 or higher
- [pnpm](https://pnpm.io/) (`npm install -g pnpm`)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/interactive-appraisal-report.git
cd interactive-appraisal-report

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser. The default password is `PEAK2026`.

---

## Customizing for a New Appraisal

All report data lives in a single file:

```
client/src/lib/appraisalData.ts
```

Open that file and update the following sections to match your appraisal:

### 1. Report Meta

```typescript
fileNo: "YOUR-FILE-NUMBER",
effectiveDate: "Month DD, YYYY",
reportDate: "Month DD, YYYY",
expirationDate: new Date("YYYY-MM-DD"), // 90 days from effective date
password: "YOUR-SECURE-PASSWORD",       // ← Change this for every client!
```

### 2. Subject Property

```typescript
subject: {
  address: "123 Main Street",
  city: "Your City",
  state: "ID",
  zip: "83000",
  county: "Jefferson",
  parcelNumber: "RP000000000000",
  lat: 43.0000,   // ← Google Maps coordinates
  lng: -112.0000,
  // ... other fields
}
```

### 3. Appraiser Profile

```typescript
appraiser: {
  name: "Your Name",
  company: "Your Appraisal Company",
  phone: "(208) 000-0000",
  email: "you@yourcompany.com",
  licenseNumber: "CRA-XXXX",
  licenseState: "ID",
  // ...
}
```

### 4. Comparable Sales

Update the `comparables` array with your 3–6 comparable sales, including all adjustments.

### 5. Market Data

Update the `marketData` object with your 1004MC data: median prices, days on market, and the price distribution from your MLS farm list.

### 6. Photos

Replace the photo URLs in `PhotoSection.tsx` with your own property photos. Upload them to any image host (Cloudinary, S3, Imgur) and paste the URLs in.

### 7. FAQ

Edit the `faq` array in `appraisalData.ts` to customize the questions and answers for your specific property and client situation.

---

## Branding Customization

To change the branding from Peak Value Appraisals to your own firm:

1. **Colors** — Edit `client/src/index.css`. The two brand colors are:
   - Navy: `#1A2F8A` (primary)
   - Cyan: `#29ABE2` (accent)

2. **Company Name** — Update `appraiser.company` in `appraisalData.ts`

3. **Logo** — Replace the SVG mountain logo in `Report.tsx` and `PasswordGate.tsx` with your own logo image or SVG

4. **Fonts** — The design uses Playfair Display (headings), IBM Plex Mono (numbers), and Source Serif 4 (body). Change the Google Fonts import in `client/index.html` to swap fonts.

---

## Password Security

The password is stored in `appraisalData.ts` and checked client-side. This is intentional — it provides a **friction barrier** that prevents casual access without requiring a backend server or database. It is not designed to protect against a determined technical attacker who inspects the source code.

**Best practices:**
- Use a unique password for every client report (e.g., `SMITH2026`, `JONES0422`)
- Deliver the password to your client separately from the link (e.g., via phone or a separate email)
- The 90-day expiration provides a natural lifecycle — the report is not meant to be a permanent archive

---

## Deployment

This is a static React app and can be deployed to any static hosting provider:

| Platform | Command |
|---|---|
| **Manus** | Click the Publish button in the Manus UI (recommended) |
| **Vercel** | `vercel deploy` |
| **Netlify** | Drag the `dist/` folder to netlify.com/drop |
| **GitHub Pages** | Use the `gh-pages` package |

To build for production:

```bash
pnpm build
# Output is in dist/
```

> **Note on Google Maps:** The map integration uses a Manus-provided proxy for the Google Maps JavaScript API. If you deploy outside of Manus, you will need to supply your own Google Maps API key. Replace the map initialization in `client/src/components/Map.tsx` with your own key.

---

## Project Structure

```
client/
  src/
    components/
      sections/          ← One file per report section (15 total)
        CoverSection.tsx
        EngagementSection.tsx
        PaymentSection.tsx
        SubjectSection.tsx
        NeighborhoodSection.tsx
        SiteSection.tsx
        MarketSection.tsx
        SalesCompSection.tsx
        CostApproachSection.tsx
        ReconciliationSection.tsx
        NarrativeSection.tsx
        PhotoSection.tsx
        SketchSection.tsx
        FAQSection.tsx
        AppraiserSection.tsx
      Map.tsx             ← Google Maps component
      SectionWrapper.tsx  ← Shared section layout wrapper
    contexts/
      AuthContext.tsx     ← Password gate state
    lib/
      appraisalData.ts    ← ⭐ ALL report data lives here
    pages/
      PasswordGate.tsx    ← Login screen
      Report.tsx          ← Main report layout + navigation
    index.css             ← Global styles + print styles
  index.html
```

---

## Contributing

Pull requests are welcome. If you are an appraiser or appraisal coach who has ideas for additional sections, features, or improvements, please open an issue first to discuss what you would like to change.

---

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

## Credits

Built with ❤️ for the appraisal profession. Inspired by the belief that appraisers deserve better tools than 30-page PDFs.

Original concept and appraisal domain expertise by **[Peak Value Appraisals](https://www.peakvalueappraisals.com)**.
