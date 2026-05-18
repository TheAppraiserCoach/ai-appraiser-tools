import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";

export default function ReconciliationSection() {
  const { finalValue, salesCompValue, costApproachValue } = reportData;

  return (
    <SectionWrapper number="10" title="Reconciliation" subtitle="Weighting of approaches and final value conclusion">
      {/* Final value hero */}
      <div className="relative rounded-xl overflow-hidden mb-5" style={{ background: "linear-gradient(135deg, #1A2F8A 0%, #0F1E5A 100%)" }}>
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `url(https://d2xsxph8kpxj0f.cloudfront.net/310419663030321591/f5bCTQ69Qyxxa5qdGUj9rt/mountain-banner-YQzEwdFcUHM9SgegiZ3ju3.webp)`,
            backgroundSize: "cover",
          }}
        />
        <div className="relative p-6 text-center">
          <div className="text-white/60 text-sm uppercase tracking-widest mb-2">Final Opinion of Market Value</div>
          <div className="text-white font-bold text-6xl font-mono mb-2">${finalValue.toLocaleString()}</div>
          <div className="text-[#29ABE2] text-sm">As of {reportData.effectiveDate} · {reportData.subject.address}, {reportData.subject.city}, {reportData.subject.state}</div>
        </div>
      </div>

      {/* Approach comparison */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        <div className="bg-white rounded-xl border-2 border-[#1A2F8A] shadow-sm p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[#1A2F8A] font-bold text-sm uppercase tracking-wider">Sales Comparison</span>
            <span className="bg-[#1A2F8A] text-white text-xs px-2 py-0.5 rounded-full">Primary</span>
          </div>
          <div className="text-[#1A2F8A] font-bold text-3xl font-mono mb-2">${salesCompValue.toLocaleString()}</div>
          <p className="text-muted-foreground text-xs">Given primary weight — most directly reflects market behavior and buyer/seller decisions. Six comparables with adjusted range of $654,200–$682,260.</p>
        </div>

        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[#1A2F8A] font-semibold text-sm uppercase tracking-wider">Cost Approach</span>
            <span className="bg-border text-muted-foreground text-xs px-2 py-0.5 rounded-full">Secondary</span>
          </div>
          <div className="text-[#1A2F8A] font-bold text-3xl font-mono mb-2">${costApproachValue.toLocaleString()}</div>
          <p className="text-muted-foreground text-xs">Given secondary weight as a reasonableness check. Replacement cost new of $581,569 minus depreciation plus land value of $97,000.</p>
        </div>
      </div>

      {/* Income approach */}
      <div className="bg-[#F8F6F1] border border-border/50 rounded-xl p-4 mb-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-muted-foreground font-semibold text-sm uppercase tracking-wider">Income Approach</span>
          <span className="bg-border/50 text-muted-foreground text-xs px-2 py-0.5 rounded-full">Not Developed</span>
        </div>
        <p className="text-muted-foreground text-xs">Not developed — the subject is owner-occupied and not typically rented in this market. The income approach is not applicable for this assignment.</p>
      </div>

      {/* Reconciliation narrative */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-5">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Reconciliation Statement</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{reportData.narrative.reconciliation}</p>
      </div>
    </SectionWrapper>
  );
}
