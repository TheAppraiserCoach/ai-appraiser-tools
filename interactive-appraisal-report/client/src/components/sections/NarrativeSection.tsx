import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";

const { narrative } = reportData;

const sections = [
  { title: "Adjustment Summary", content: narrative.adjustmentSummary },
  { title: "Highest and Best Use", content: narrative.highestAndBestUse },
  { title: "Scope of Work", content: narrative.scopeOfWork },
  { title: "Limiting Conditions & Assumptions", content: narrative.limitingConditions },
  { title: "Reconciliation", content: narrative.reconciliation },
];

export default function NarrativeSection() {
  return (
    <SectionWrapper number="11" title="Narrative & Addenda" subtitle="Appraiser's written analysis, scope of work, and limiting conditions">
      <div className="space-y-4">
        {sections.map((s, i) => (
          <div key={i} className="bg-white rounded-xl border border-border shadow-sm p-5">
            <h3 className="font-semibold text-[#1A2F8A] text-sm uppercase tracking-wider mb-3 pb-2 border-b border-border/50 flex items-center gap-2">
              <span className="w-5 h-5 rounded bg-[#1A2F8A] text-[#29ABE2] text-xs font-mono flex items-center justify-center shrink-0">
                {String(i + 1)}
              </span>
              {s.title}
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed" style={{ fontFamily: "'Source Serif 4', serif" }}>
              {s.content}
            </p>
          </div>
        ))}
      </div>

      {/* Certification */}
      <div className="mt-4 bg-[#1A2F8A]/5 border border-[#1A2F8A]/20 rounded-xl p-5">
        <h3 className="font-semibold text-[#1A2F8A] text-sm uppercase tracking-wider mb-3">Appraiser Certification</h3>
        <p className="text-sm text-muted-foreground leading-relaxed mb-3">
          I certify that, to the best of my knowledge and belief: the statements of fact contained in this report are true and correct; the reported analyses, opinions, and conclusions are limited only by the reported assumptions and limiting conditions and are my personal, impartial, and unbiased professional analyses, opinions, and conclusions; I have no present or prospective interest in the property that is the subject of this report, and I have no personal interest with respect to the parties involved.
        </p>
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-[#1A2F8A]/20">
          <div>
            <div className="text-muted-foreground text-xs">Appraiser</div>
            <div className="font-semibold text-[#1A2F8A]">{reportData.appraiser.name}</div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs">License</div>
            <div className="font-mono font-semibold text-[#1A2F8A]">{reportData.appraiser.licenseNumber} ({reportData.appraiser.licenseState})</div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs">Signature Date</div>
            <div className="font-semibold text-[#1A2F8A]">{reportData.appraiser.signatureDate}</div>
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}
