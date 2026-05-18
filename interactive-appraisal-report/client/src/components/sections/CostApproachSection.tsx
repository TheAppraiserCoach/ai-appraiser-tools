import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const { costApproach: ca } = reportData;

const costBreakdown = [
  { name: "Dwelling", value: ca.dwelling.total, color: "#1A2F8A" },
  { name: "Basement", value: ca.basement.total, color: "#2A4BA0" },
  { name: "Garage", value: ca.garage.total, color: "#29ABE2" },
  { name: "Amenities", value: ca.otherAmenities, color: "#6BBFE8" },
];

export default function CostApproachSection() {
  return (
    <SectionWrapper number="09" title="Cost Approach" subtitle="Replacement cost new, depreciation, and land value — DwellingCost.com data">
      {/* Indicated value */}
      <div className="bg-[#1A2F8A] rounded-xl p-5 mb-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <div className="text-white/60 text-xs uppercase tracking-wider mb-1">Indicated Value by Cost Approach</div>
          <div className="text-white font-bold text-4xl font-mono">${ca.indicatedValueByCostApproach.toLocaleString()}</div>
        </div>
        <div className="text-right">
          <div className="text-white/60 text-xs mb-1">Source</div>
          <div className="text-[#29ABE2] font-semibold text-sm">DwellingCost.com</div>
          <div className="text-white/40 text-xs mt-1">Data as of April 7, 2026</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        {/* Cost breakdown chart */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm mb-1">Cost New Breakdown</h3>
          <p className="text-muted-foreground text-xs mb-4">Component costs before depreciation</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={costBreakdown} layout="vertical" margin={{ top: 0, right: 60, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
              <XAxis type="number" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} tick={{ fontSize: 9, fill: "#9CA3AF" }} tickLine={false} axisLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#374151" }} tickLine={false} axisLine={false} width={70} />
              <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} label={{ position: "right", formatter: (v: number) => `$${(v / 1000).toFixed(0)}K`, fontSize: 10, fill: "#6B7280" }}>
                {costBreakdown.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost calculation */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm mb-4">Cost Calculation</h3>
          <div className="space-y-2">
            {[
              { label: "Dwelling", sub: `${ca.dwelling.sqft.toLocaleString()} sf × $${ca.dwelling.ratePerSF}/sf`, value: ca.dwelling.total, indent: false },
              { label: "Basement", sub: `${ca.basement.sqft.toLocaleString()} sf × $${ca.basement.ratePerSF}/sf`, value: ca.basement.total, indent: false },
              { label: "Garage", sub: `${ca.garage.sqft} sf × $${ca.garage.ratePerSF}/sf`, value: ca.garage.total, indent: false },
              { label: "Other Amenities", sub: "Fireplace, landscaping, etc.", value: ca.otherAmenities, indent: false },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center py-1.5 border-b border-border/30">
                <div>
                  <div className="text-sm font-medium">{row.label}</div>
                  <div className="text-xs text-muted-foreground font-mono">{row.sub}</div>
                </div>
                <div className="font-mono font-semibold text-sm text-[#1A2F8A]">${row.value.toLocaleString()}</div>
              </div>
            ))}
            <div className="flex justify-between items-center py-2 border-b-2 border-[#1A2F8A]/30">
              <span className="font-bold text-sm">Total Cost New</span>
              <span className="font-mono font-bold text-[#1A2F8A]">${ca.totalCostNew.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/30">
              <div>
                <div className="text-sm">Less: Physical Depreciation</div>
                <div className="text-xs text-muted-foreground">Effective age {reportData.improvements.effectiveAge}yr / Economic life {ca.remainingEconomicLife + reportData.improvements.effectiveAge}yr</div>
              </div>
              <div className="font-mono font-semibold text-sm text-red-500">-${ca.physicalDepreciation.toLocaleString()}</div>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/30">
              <span className="text-sm">Depreciated Cost of Improvements</span>
              <span className="font-mono font-semibold text-sm">${ca.depreciatedCostOfImprovements.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/30">
              <span className="text-sm">Site Value (Land)</span>
              <span className="font-mono font-semibold text-sm">${ca.siteValue.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/30">
              <span className="text-sm">Site Improvements</span>
              <span className="font-mono font-semibold text-sm">${ca.siteImprovements.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center py-2 bg-[#1A2F8A]/5 rounded-lg px-2 mt-1">
              <span className="font-bold text-[#1A2F8A]">Indicated Value</span>
              <span className="font-mono font-bold text-xl text-[#1A2F8A]">${ca.indicatedValueByCostApproach.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* DwellingCost.com rates */}
      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="bg-[#1A2F8A] px-4 py-2.5">
          <span className="text-white font-semibold text-sm">DwellingCost.com — Replacement Cost Rates</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#F8F6F1] border-b border-border">
                <th className="text-left px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Component</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Size</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Rate/SF</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Total</th>
              </tr>
            </thead>
            <tbody>
              {[
                { comp: "Dwelling (Above Grade)", size: `${ca.dwelling.sqft.toLocaleString()} sf`, rate: `$${ca.dwellingCostPerSF}/sf`, total: ca.dwellingTotal },
                { comp: "Garage", size: `${ca.garage.sqft} sf`, rate: `$${ca.garageCostPerSF}/sf`, total: ca.garageTotal },
                { comp: "Basement", size: `${ca.basement.sqft.toLocaleString()} sf`, rate: `$${ca.basementCostPerSF}/sf`, total: ca.basementTotal },
              ].map((row, i) => (
                <tr key={i} className="border-b border-border/40">
                  <td className="px-4 py-2.5">{row.comp}</td>
                  <td className="px-4 py-2.5 text-right font-mono">{row.size}</td>
                  <td className="px-4 py-2.5 text-right font-mono">{row.rate}</td>
                  <td className="px-4 py-2.5 text-right font-mono font-semibold text-[#1A2F8A]">${row.total.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-2 bg-[#F8F6F1] border-t border-border text-xs text-muted-foreground">
          Quality Rating: {ca.qualityRating} · Data Effective: {ca.effectiveDateOfCostData}
        </div>
      </div>
    </SectionWrapper>
  );
}
