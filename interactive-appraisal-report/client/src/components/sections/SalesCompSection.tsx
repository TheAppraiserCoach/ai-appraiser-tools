import { useState } from "react";
import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { ChevronDown, ChevronUp } from "lucide-react";

const { comparables, finalValue, subject, improvements } = reportData;

export default function SalesCompSection() {
  const [expandedComp, setExpandedComp] = useState<number | null>(null);

  const chartData = comparables.map((c) => ({
    name: `Comp ${c.id}`,
    salePrice: c.salePrice,
    adjustedPrice: c.adjustedPrice,
  }));

  return (
    <SectionWrapper number="08" title="Sales Comparison Approach" subtitle="Six comparable sales analyzed and adjusted to indicate subject value">
      {/* Value indication */}
      <div className="bg-[#1A2F8A] rounded-xl p-5 mb-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <div className="text-white/60 text-xs uppercase tracking-wider mb-1">Indicated Value by Sales Comparison</div>
          <div className="text-white font-bold text-4xl font-mono">${finalValue.toLocaleString()}</div>
        </div>
        <div className="text-right">
          <div className="text-white/60 text-xs mb-1">Adjusted Range</div>
          <div className="text-[#29ABE2] font-mono font-semibold">
            ${Math.min(...comparables.map(c => c.adjustedPrice)).toLocaleString()} – ${Math.max(...comparables.map(c => c.adjustedPrice)).toLocaleString()}
          </div>
          <div className="text-white/40 text-xs mt-1">{comparables.length} comparables analyzed</div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-5 mb-5">
        <h3 className="font-semibold text-[#1A2F8A] text-sm mb-1">Sale Price vs. Adjusted Price</h3>
        <p className="text-muted-foreground text-xs mb-4">Navy = unadjusted sale price · Cyan = adjusted price · Dashed line = final value</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#9CA3AF" }} tickLine={false} />
            <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} tick={{ fontSize: 10, fill: "#9CA3AF" }} tickLine={false} axisLine={false} domain={[580000, 720000]} />
            <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
            <ReferenceLine y={finalValue} stroke="#29ABE2" strokeDasharray="5 3" label={{ value: `Final $${(finalValue / 1000).toFixed(0)}K`, fill: "#29ABE2", fontSize: 10, position: "insideTopRight" }} />
            <Bar dataKey="salePrice" fill="#1A2F8A" opacity={0.6} radius={[3, 3, 0, 0]} name="Sale Price" />
            <Bar dataKey="adjustedPrice" fill="#29ABE2" radius={[3, 3, 0, 0]} name="Adjusted Price" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Comparables table */}
      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden mb-4">
        <div className="bg-[#1A2F8A] px-4 py-2.5 flex items-center justify-between">
          <span className="text-white font-semibold text-sm">Comparable Sales Grid</span>
          <span className="text-white/50 text-xs">Click any row to expand adjustments</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#F8F6F1] border-b border-border">
                <th className="text-left px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">#</th>
                <th className="text-left px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">Address</th>
                <th className="text-right px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">Sale Price</th>
                <th className="text-right px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">GLA</th>
                <th className="text-right px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">$/SF</th>
                <th className="text-right px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider">Net Adj</th>
                <th className="text-right px-3 py-2 text-xs text-muted-foreground uppercase tracking-wider font-bold text-[#1A2F8A]">Adj Price</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {/* Subject row */}
              <tr className="bg-[#1A2F8A]/5 border-b border-border">
                <td className="px-3 py-2.5 font-semibold text-[#1A2F8A]">S</td>
                <td className="px-3 py-2.5">
                  <div className="font-semibold text-[#1A2F8A]">{subject.address}</div>
                  <div className="text-xs text-muted-foreground">{subject.city}, {subject.state} · SUBJECT</div>
                </td>
                <td className="px-3 py-2.5 text-right font-mono text-[#1A2F8A] font-bold">${finalValue.toLocaleString()}</td>
                <td className="px-3 py-2.5 text-right font-mono">{improvements.grossLivingArea.toLocaleString()}</td>
                <td className="px-3 py-2.5 text-right font-mono">${(finalValue / improvements.grossLivingArea).toFixed(2)}</td>
                <td className="px-3 py-2.5 text-right">—</td>
                <td className="px-3 py-2.5 text-right font-mono font-bold text-[#1A2F8A]">${finalValue.toLocaleString()}</td>
                <td className="px-3 py-2.5"></td>
              </tr>

              {comparables.map((c) => (
                <>
                  <tr
                    key={c.id}
                    className="border-b border-border/40 hover:bg-[#F8F6F1] cursor-pointer transition-colors"
                    onClick={() => setExpandedComp(expandedComp === c.id ? null : c.id)}
                  >
                    <td className="px-3 py-2.5 font-mono text-[#29ABE2] font-semibold">{c.id}</td>
                    <td className="px-3 py-2.5">
                      <div className="font-medium">{c.address}</div>
                      <div className="text-xs text-muted-foreground">{c.proximity} · {c.saleDate}</div>
                    </td>
                    <td className="px-3 py-2.5 text-right font-mono">${c.salePrice.toLocaleString()}</td>
                    <td className="px-3 py-2.5 text-right font-mono">{c.gla.toLocaleString()}</td>
                    <td className="px-3 py-2.5 text-right font-mono">${c.salePricePerSF.toFixed(2)}</td>
                    <td className={`px-3 py-2.5 text-right font-mono font-semibold ${c.netAdjustment > 0 ? "text-emerald-600" : c.netAdjustment < 0 ? "text-red-500" : "text-muted-foreground"}`}>
                      {c.netAdjustment > 0 ? "+" : ""}{c.netAdjustment.toLocaleString()}
                    </td>
                    <td className="px-3 py-2.5 text-right font-mono font-bold text-[#1A2F8A]">${c.adjustedPrice.toLocaleString()}</td>
                    <td className="px-3 py-2.5 text-center">
                      {expandedComp === c.id ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                    </td>
                  </tr>

                  {expandedComp === c.id && (
                    <tr key={`${c.id}-detail`} className="bg-[#F8F6F1]">
                      <td colSpan={8} className="px-4 py-4">
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                          {[
                            { label: "MLS #", value: c.mlsNumber },
                            { label: "Financing", value: c.financing },
                            { label: "Concessions", value: c.concessions ? `$${c.concessions.toLocaleString()}` : "None" },
                            { label: "DOM", value: `${c.daysOnMarket} days` },
                            { label: "Bedrooms", value: String(c.bedrooms) },
                            { label: "Bathrooms", value: c.bathrooms },
                            { label: "Condition", value: c.condition },
                            { label: "Quality", value: c.quality },
                            { label: "Garage", value: c.garage },
                            { label: "Site", value: c.siteArea },
                            { label: "Fireplace", value: String(c.fireplace) },
                            { label: "Sprinkler", value: c.sprinkler ? "Yes" : "No" },
                          ].map((item) => (
                            <div key={item.label} className="bg-white rounded-lg p-2 border border-border/40">
                              <div className="text-muted-foreground text-xs">{item.label}</div>
                              <div className="font-mono text-sm font-medium mt-0.5">{item.value}</div>
                            </div>
                          ))}
                        </div>
                        <div className="mt-3 grid grid-cols-3 sm:grid-cols-6 gap-2">
                          {Object.entries(c.adjustments)
                            .filter(([, v]) => v !== 0)
                            .map(([key, val]) => (
                              <div key={key} className={`rounded-lg p-2 border text-center ${(val as number) > 0 ? "bg-emerald-50 border-emerald-200" : "bg-red-50 border-red-200"}`}>
                                <div className="text-xs text-muted-foreground capitalize">{key}</div>
                                <div className={`font-mono text-sm font-semibold ${(val as number) > 0 ? "text-emerald-700" : "text-red-600"}`}>
                                  {(val as number) > 0 ? "+" : ""}{(val as number).toLocaleString()}
                                </div>
                              </div>
                            ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-muted-foreground text-xs text-center">
        All comparables are single-family residential properties in the Rigby, ID market area. Adjustments reflect paired sales analysis.
      </p>
    </SectionWrapper>
  );
}
