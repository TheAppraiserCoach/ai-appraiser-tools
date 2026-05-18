import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";

const { marketData } = reportData;

const formatPrice = (v: number) => `$${(v / 1000).toFixed(0)}K`;

export default function MarketSection() {
  return (
    <SectionWrapper number="07" title="Market Analysis" subtitle="Market conditions, price trends, and supply/demand analysis for the Rigby, ID market">
      {/* Summary stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {[
          { label: "Prior 12 Mo Sales", value: String(marketData.priorYear.sales), sub: "transactions" },
          { label: "Current Median", value: `$${(marketData.current3Mo.medianPrice / 1000).toFixed(0)}K`, sub: "3-month median" },
          { label: "Median DOM", value: String(marketData.current3Mo.medianDOM), sub: "days on market" },
          { label: "List-to-Sale", value: `${(marketData.listToSaleRatio * 100).toFixed(1)}%`, sub: "avg ratio" },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-xl border border-border shadow-sm p-4 text-center">
            <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">{item.label}</div>
            <div className="text-[#1A2F8A] font-bold text-2xl font-mono">{item.value}</div>
            <div className="text-muted-foreground text-xs mt-0.5">{item.sub}</div>
          </div>
        ))}
      </div>

      {/* Price trend chart */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-5 mb-5">
        <h3 className="font-semibold text-[#1A2F8A] text-sm mb-1">Median Sale Price Trend</h3>
        <p className="text-muted-foreground text-xs mb-4">Monthly median sale price — Rigby, ID market area (Jul 2025 – Apr 2026)</p>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={marketData.monthlyTrend} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1A2F8A" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#1A2F8A" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#9CA3AF" }} tickLine={false} />
            <YAxis tickFormatter={formatPrice} tick={{ fontSize: 10, fill: "#9CA3AF" }} tickLine={false} axisLine={false} />
            <Tooltip
              formatter={(v: number) => [`$${v.toLocaleString()}`, "Median Price"]}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #E5E7EB" }}
            />
            <ReferenceLine y={664000} stroke="#29ABE2" strokeDasharray="4 2" label={{ value: "Subject $664K", fill: "#29ABE2", fontSize: 10, position: "right" }} />
            <Area type="monotone" dataKey="medianPrice" stroke="#1A2F8A" strokeWidth={2} fill="url(#priceGrad)" dot={{ fill: "#1A2F8A", r: 3 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-5">
        {/* DOM chart */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm mb-1">Days on Market</h3>
          <p className="text-muted-foreground text-xs mb-3">Average DOM by month</p>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={marketData.monthlyTrend} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 9, fill: "#9CA3AF" }} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: "#9CA3AF" }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
              <Bar dataKey="dom" fill="#29ABE2" radius={[3, 3, 0, 0]} name="Days on Market" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Price distribution */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm mb-1">Price Distribution</h3>
          <p className="text-muted-foreground text-xs mb-3">Sales by price range (farm list, 37 sales)</p>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={marketData.priceDistribution} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
              <XAxis dataKey="range" tick={{ fontSize: 8, fill: "#9CA3AF" }} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: "#9CA3AF" }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} />
              <Bar dataKey="count" fill="#1A2F8A" radius={[3, 3, 0, 0]} name="# of Sales" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Period comparison table */}
      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="bg-[#1A2F8A] px-4 py-2.5">
          <span className="text-white font-semibold text-sm">Market Conditions Summary (1004MC)</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#F8F6F1] border-b border-border">
                <th className="text-left px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Period</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Sales</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Median Price</th>
                <th className="text-right px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider">Median DOM</th>
              </tr>
            </thead>
            <tbody>
              {[
                { period: "Prior 12 Months", ...marketData.priorYear },
                { period: "Prior 6 Months", ...marketData.prior6Mo },
                { period: "Current 3 Months", ...marketData.current3Mo },
              ].map((row, i) => (
                <tr key={i} className={`border-b border-border/40 ${i === 2 ? "bg-[#29ABE2]/5 font-semibold" : ""}`}>
                  <td className="px-4 py-2.5 text-sm">{row.period}</td>
                  <td className="px-4 py-2.5 text-right font-mono">{row.sales}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-[#1A2F8A]">${row.medianPrice.toLocaleString()}</td>
                  <td className="px-4 py-2.5 text-right font-mono">{row.medianDOM} days</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-2 bg-[#F8F6F1] border-t border-border text-xs text-muted-foreground">
          Trend: <strong className="text-[#1A2F8A]">{marketData.trend}</strong> · Supply/Demand: <strong className="text-[#1A2F8A]">{marketData.supplyDemand}</strong>
        </div>
      </div>
    </SectionWrapper>
  );
}
