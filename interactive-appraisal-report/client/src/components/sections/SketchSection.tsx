import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";

const { improvements } = reportData;

// ─────────────────────────────────────────────────────────────────────────────
// SVG Floor Plan — rebuilt from actual Building Sketch (appraisal page 16)
// Scale: 1 ft = 8px  |  Canvas: 720 × 640
//
// FIRST FLOOR (solid, top section of sketch):
//   Main rectangle: 29' wide × 33' deep  → origin (80, 60) → (312, 324)
//   Right extension: 12+2+11+12+2 = 39' wide × 33' deep → (312, 60) → (624, 324)
//     but right side has a 5' notch cut at top-right: (579, 60)→(624, 60)→(624, 220)→(579, 220)
//   So first floor main polygon (upper body):
//     (80,60)→(579,60)→(579,220)→(624,220)→(624,324)→(80,324)
//
// LOWER PROTRUSION (south, attached to main body):
//   Left: Bedroom + Bath wing: 21' wide × 21' deep → (80,324)→(248,324)→(248,492)→(80,492)
//   Covered Porch: 21' wide × 6' deep → (80,492)→(248,492)→(248,540)→(80,540)
//   Steps: small notch left of porch
//
// GARAGE (right side, south):
//   Main garage body: 26' wide × 22' deep → (312,324)→(520,324)→(520,500)→(312,500)
//     Wait — garage is 26×22 + 22×15 = 902sf
//     Upper garage: 26' deep × 22' wide... looking at sketch:
//     The garage extends right from ~center, 22' wide (E-W), 26' deep (N-S) = 572sf
//     Then a lower step: 22' wide × 15' deep = 330sf
//     Garage left edge aligns with center of main body
//   Garage: x=312 to x=488 (22'×8=176px wide), y=324 to y=532 (26'×8=208px deep)
//   Lower step: x=312 to x=488, y=532 to y=652 (15'×8=120px) — too tall, adjust
//   Use: main garage 22' wide × 26' deep + step 22' wide × 15' deep
//     Garage: (312,324)→(488,324)→(488,532)→(312,532)
//     Step:   (312,532)→(488,532)→(488,652)→(312,652) — clipped at canvas
//
// BASEMENT (dashed, lower half of sketch, same footprint as first floor):
//   Main rect: 66' wide × 20' deep → (80,380)→(608,380)→(608,540)→(80,540)
//   Lower section: 34' wide × 33' deep → (80,540)→(352,540)→(352,804)→(80,804)
//   Lower notch: 21' wide × 15' deep → (80,804)→(248,804)→(248,924)→(80,924)
//   (basement is shown below first floor in the original sketch, separate drawing)
// ─────────────────────────────────────────────────────────────────────────────

export default function SketchSection() {
  return (
    <SectionWrapper number="13" title="Building Sketch" subtitle="Floor plan dimensions and area calculations per ANSI standards">
      {/* Area summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {[
          { label: "Above Grade GLA", value: `${improvements.grossLivingArea.toLocaleString()} sf` },
          { label: "Basement Area", value: "1,804 sf" },
          { label: "Garage Area", value: `${improvements.garageArea} sf` },
          { label: "Cov. Porch", value: "126 sf" },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-lg border border-border shadow-sm p-3 text-center">
            <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">{item.label}</div>
            <div className="text-[#1A2F8A] font-bold text-xl font-mono">{item.value}</div>
          </div>
        ))}
      </div>

      {/* SVG Sketch */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-5 mb-4 overflow-x-auto">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-1">Building Sketch — 4067 E 518 N</h3>
        <p className="text-muted-foreground text-xs mb-4">Scale: 1 ft ≈ 8 px &nbsp;|&nbsp; Sketch by a la mode / TOTAL</p>
        <div className="flex justify-center">
          {/*
            LAYOUT ANALYSIS from actual sketch:
            ┌─────────────────────────────────────────────────────┐
            │  29'        │  Dining  │  11' │  Primary Bedroom 2' │
            │  Bedroom    │  Living  │      │                     │
            │  Bath  ─────────────── Kitchen ──── Laundry  ½Bath  │
            │             │  First Floor [1732]                   │
            │  Bedroom    │  21'                                  │
            │  ┌──Porch──┐│  │  ┌──────────────────────────────┐ │
            │  │ 21'×6'  ││  │  │   3 Car Attached [902 sf]    │ │
            └──┴─────────┴┴──┴──┴──────────────────────────────┘

            Scale: 8px/ft
            Canvas: 760 wide × 560 tall (first floor only)
            Origin: (60, 50)

            First floor main body:
              Left section (29' wide × 33' deep): x=60→292, y=50→314
              Right section (29'+12+2+11+12+2=68' wide, but right notch 5' cut):
                Full right: x=292→628, y=50→314
                Notch (5' wide × 20' deep on top-right): cut x=588→628, y=50→210
              So first floor polygon:
                (60,50)→(588,50)→(588,210)→(628,210)→(628,314)→(60,314)

            Lower bedroom wing (21' wide × 21' deep):
              x=60→228, y=314→482

            Covered Porch (21' wide × 6' deep):
              x=60→228, y=482→530

            Garage (attached right side):
              Upper: 26'×22' = 572sf → x=292→468 (22'×8=176), y=314→522 (26'×8=208)
              Lower step: 22'×15' = 330sf → x=292→468, y=522→642
              Total garage: x=292→468, y=314→642
          */}
          <svg
            width="100%"
            viewBox="0 0 760 660"
            style={{ maxWidth: 760, fontFamily: "'IBM Plex Mono', monospace" }}
          >
            <defs>
              <marker id="sk-arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 z" fill="#9CA3AF" />
              </marker>
              <marker id="sk-arrl" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse">
                <path d="M0,0 L6,3 L0,6 z" fill="#9CA3AF" />
              </marker>
            </defs>

            {/* Canvas background */}
            <rect width="760" height="660" fill="#F9F8F5" rx="6" />

            {/* ── FIRST FLOOR (solid blue fill, irregular polygon) ── */}
            {/* Main body: left 29'×33' + right 39'×33' with top-right notch */}
            <polygon
              points="60,50 588,50 588,210 628,210 628,314 60,314"
              fill="#DDE5F5"
              stroke="#1A2F8A"
              strokeWidth="2.5"
            />

            {/* ── Interior dividers (First Floor) ── */}
            {/* Vertical: left bedroom section at 29' from left = 60+232=292 */}
            <line x1="292" y1="50" x2="292" y2="314" stroke="#1A2F8A" strokeWidth="1.2" strokeDasharray="5 3" opacity="0.55" />
            {/* Horizontal: upper rooms / lower utility at ~20' deep = 50+160=210 */}
            <line x1="60" y1="210" x2="628" y2="210" stroke="#1A2F8A" strokeWidth="1.2" strokeDasharray="5 3" opacity="0.55" />
            {/* Vertical: primary bedroom at 29+12+2+11=54' from left = 60+432=492 */}
            <line x1="492" y1="50" x2="492" y2="210" stroke="#1A2F8A" strokeWidth="1" strokeDasharray="4 3" opacity="0.45" />
            {/* Vertical: laundry/half-bath divider at ~32' from right = 628-32×8=372 */}
            <line x1="500" y1="210" x2="500" y2="314" stroke="#1A2F8A" strokeWidth="1" strokeDasharray="4 3" opacity="0.45" />
            {/* Vertical: kitchen/pantry at center ~6' wide notch */}
            <line x1="380" y1="210" x2="380" y2="314" stroke="#1A2F8A" strokeWidth="1" strokeDasharray="4 3" opacity="0.35" />

            {/* ── Room labels (First Floor upper) ── */}
            <text x="176" y="115" textAnchor="middle" fill="#1A2F8A" fontSize="11" fontWeight="600">Bedroom</text>
            <text x="176" y="165" textAnchor="middle" fill="#1A2F8A" fontSize="10">Living</text>
            <text x="390" y="100" textAnchor="middle" fill="#1A2F8A" fontSize="10" fontWeight="600">Dining</text>
            <text x="540" y="100" textAnchor="middle" fill="#1A2F8A" fontSize="10" fontWeight="600">Primary</text>
            <text x="540" y="114" textAnchor="middle" fill="#1A2F8A" fontSize="10" fontWeight="600">Bedroom</text>
            <text x="540" y="165" textAnchor="middle" fill="#1A2F8A" fontSize="9">Primary Bath</text>

            {/* ── Room labels (First Floor lower strip) ── */}
            <text x="176" y="268" textAnchor="middle" fill="#1A2F8A" fontSize="9" fontWeight="600">Bath</text>
            <text x="330" y="255" textAnchor="middle" fill="#1A2F8A" fontSize="9" fontWeight="600">Kitchen</text>
            <text x="330" y="290" textAnchor="middle" fill="#6B7280" fontSize="8">Pantry</text>
            <text x="440" y="268" textAnchor="middle" fill="#1A2F8A" fontSize="9" fontWeight="600">Laundry</text>
            <text x="564" y="268" textAnchor="middle" fill="#1A2F8A" fontSize="9" fontWeight="600">½ Bath</text>

            {/* First Floor center label */}
            <text x="340" y="148" textAnchor="middle" fill="#1A2F8A" fontSize="12" fontWeight="700">First Floor</text>
            <text x="340" y="165" textAnchor="middle" fill="#29ABE2" fontSize="11">[1,732 Sq ft]</text>

            {/* ── LOWER BEDROOM WING (21'×21') ── */}
            <rect x="60" y="314" width="168" height="168" fill="#DDE5F5" stroke="#1A2F8A" strokeWidth="2.5" />
            <text x="144" y="385" textAnchor="middle" fill="#1A2F8A" fontSize="10" fontWeight="600">Bedroom</text>
            <text x="88" y="420" textAnchor="middle" fill="#1A2F8A" fontSize="9">Bath</text>

            {/* ── COVERED PORCH (21'×6') ── */}
            <rect x="60" y="482" width="168" height="48" fill="#EBF0FA" stroke="#1A2F8A" strokeWidth="1.5" strokeDasharray="5 3" />
            <text x="144" y="508" textAnchor="middle" fill="#6B7280" fontSize="9">Cov Porch</text>
            <text x="144" y="521" textAnchor="middle" fill="#6B7280" fontSize="8">[126 Sq ft]</text>

            {/* Steps (small rectangles left of porch) */}
            <rect x="36" y="468" width="24" height="14" fill="#D8E3F0" stroke="#1A2F8A" strokeWidth="1" />
            <rect x="40" y="482" width="18" height="10" fill="#D8E3F0" stroke="#1A2F8A" strokeWidth="1" />

            {/* ── GARAGE (3-Car Attached) ── */}
            {/* Upper: 22'×26' = 572sf → width=176, height=208 */}
            <rect x="292" y="314" width="176" height="208" fill="#EEF2F8" stroke="#1A2F8A" strokeWidth="2" />
            {/* Lower step: 22'×15' = 330sf → width=176, height=120 */}
            <rect x="292" y="522" width="176" height="120" fill="#EEF2F8" stroke="#1A2F8A" strokeWidth="2" />

            {/* Garage door lines (3 bays) */}
            <line x1="292" y1="360" x2="468" y2="360" stroke="#1A2F8A" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.4" />
            <line x1="292" y1="406" x2="468" y2="406" stroke="#1A2F8A" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.4" />
            <line x1="292" y1="452" x2="468" y2="452" stroke="#1A2F8A" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.4" />
            {/* Vertical bay dividers */}
            <line x1="351" y1="314" x2="351" y2="522" stroke="#1A2F8A" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.3" />
            <line x1="410" y1="314" x2="410" y2="522" stroke="#1A2F8A" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.3" />

            <text x="380" y="420" textAnchor="middle" fill="#1A2F8A" fontSize="11" fontWeight="700">3 Car Attached</text>
            <text x="380" y="436" textAnchor="middle" fill="#29ABE2" fontSize="10">[902 Sq ft]</text>

            {/* ── BASEMENT (dashed overlay, shown separately below) ── */}
            {/* Basement mirrors the footprint of first floor + lower wing */}
            <text x="380" y="610" textAnchor="middle" fill="#29ABE2" fontSize="10" fontWeight="600">Basement [1,804 Sq ft] — see area calculations below</text>

            {/* ── DIMENSION LINES ── */}
            {/* Top width: 29' left section */}
            <line x1="60" y1="34" x2="292" y2="34" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="176" y="28" textAnchor="middle" fill="#6B7280" fontSize="9">29'</text>

            {/* Right section width */}
            <line x1="292" y1="34" x2="588" y2="34" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="440" y="28" textAnchor="middle" fill="#6B7280" fontSize="9">37'</text>

            {/* Notch: 5' */}
            <line x1="588" y1="34" x2="628" y2="34" stroke="#9CA3AF" strokeWidth="0.8" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="608" y="28" textAnchor="middle" fill="#6B7280" fontSize="8">5'</text>

            {/* Left height: 33' */}
            <line x1="42" y1="50" x2="42" y2="314" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="30" y="185" textAnchor="middle" fill="#6B7280" fontSize="9" transform="rotate(-90 30 185)">33'</text>

            {/* Lower wing height: 21' */}
            <line x1="42" y1="314" x2="42" y2="482" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="30" y="400" textAnchor="middle" fill="#6B7280" fontSize="9" transform="rotate(-90 30 400)">21'</text>

            {/* Lower wing width: 21' */}
            <line x1="60" y1="540" x2="228" y2="540" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="144" y="554" textAnchor="middle" fill="#6B7280" fontSize="9">21'</text>

            {/* Garage width: 22' */}
            <line x1="292" y1="298" x2="468" y2="298" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="380" y="292" textAnchor="middle" fill="#6B7280" fontSize="9">22'</text>

            {/* Garage upper height: 26' */}
            <line x1="482" y1="314" x2="482" y2="522" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="496" y="420" textAnchor="middle" fill="#6B7280" fontSize="9" transform="rotate(90 496 420)">26'</text>

            {/* Garage lower step: 15' */}
            <line x1="482" y1="522" x2="482" y2="642" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="496" y="584" textAnchor="middle" fill="#6B7280" fontSize="9" transform="rotate(90 496 584)">15'</text>

            {/* Right notch depth: 20' */}
            <line x1="642" y1="50" x2="642" y2="210" stroke="#9CA3AF" strokeWidth="1" markerEnd="url(#sk-arr)" markerStart="url(#sk-arrl)" />
            <text x="658" y="132" textAnchor="middle" fill="#6B7280" fontSize="9" transform="rotate(90 658 132)">20'</text>

            {/* ── NORTH ARROW ── */}
            <g transform="translate(700, 44)">
              <circle cx="0" cy="0" r="18" fill="white" stroke="#1A2F8A" strokeWidth="1.5" />
              <polygon points="0,-14 4,4 0,0 -4,4" fill="#1A2F8A" />
              <polygon points="0,14 4,-4 0,0 -4,-4" fill="#D1D5DB" />
              <text x="0" y="5" textAnchor="middle" fontSize="12" fill="#1A2F8A" fontWeight="bold">N</text>
            </g>

            {/* ── LEGEND ── */}
            <rect x="60" y="580" width="14" height="10" fill="#DDE5F5" stroke="#1A2F8A" strokeWidth="1.5" />
            <text x="80" y="590" fill="#6B7280" fontSize="9">First Floor / Lower Wing</text>
            <rect x="240" y="580" width="14" height="10" fill="#EEF2F8" stroke="#1A2F8A" strokeWidth="1.5" />
            <text x="260" y="590" fill="#6B7280" fontSize="9">Garage</text>
            <rect x="320" y="580" width="14" height="10" fill="#EBF0FA" stroke="#1A2F8A" strokeWidth="1.5" strokeDasharray="4 2" />
            <text x="340" y="590" fill="#6B7280" fontSize="9">Covered Porch</text>
          </svg>
        </div>
        <p className="text-muted-foreground text-xs text-center mt-3">
          Sketch based on appraiser field measurements. Area calculations per ANSI Z765-2021. Not to scale.
        </p>
      </div>

      {/* Area Calculations Table */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-4 mb-4">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Area Calculations Summary</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted-foreground font-medium text-xs uppercase">Area</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs uppercase">Sq Ft</th>
              <th className="text-right py-2 text-muted-foreground font-medium text-xs uppercase">Calculation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            <tr>
              <td className="py-2 font-medium text-[#1A2F8A]">First Floor (GLA)</td>
              <td className="py-2 text-right font-mono font-bold">1,732</td>
              <td className="py-2 text-right text-muted-foreground text-xs font-mono">12×2 + 12×2 + 6×1 + 34×29 + 13×4</td>
            </tr>
            <tr>
              <td className="py-2 font-medium text-[#29ABE2]">Basement</td>
              <td className="py-2 text-right font-mono font-bold text-[#29ABE2]">1,804</td>
              <td className="py-2 text-right text-muted-foreground text-xs font-mono">20×32 + 34×33 + 2×21</td>
            </tr>
            <tr>
              <td className="py-2 font-medium text-slate-600">Covered Porch</td>
              <td className="py-2 text-right font-mono">126</td>
              <td className="py-2 text-right text-muted-foreground text-xs font-mono">21×6</td>
            </tr>
            <tr>
              <td className="py-2 font-medium text-slate-600">3-Car Attached Garage</td>
              <td className="py-2 text-right font-mono">902</td>
              <td className="py-2 text-right text-muted-foreground text-xs font-mono">26×22 + 22×15</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="bg-[#1A2F8A]/5 border border-[#1A2F8A]/15 rounded-xl p-4">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-2">ANSI Measurement Standards</h3>
        <p className="text-muted-foreground text-xs leading-relaxed">
          Gross Living Area (GLA) of 1,732 sf includes only above-grade finished living space per ANSI Z765-2021. The basement (1,804 sf, fully finished) is separately noted and valued but excluded from GLA. The 3-car attached garage (902 sf) and covered porch (126 sf) are non-living areas. All measurements were rounded to the nearest half-foot.
        </p>
      </div>
    </SectionWrapper>
  );
}
