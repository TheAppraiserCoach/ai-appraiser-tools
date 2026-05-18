import { useState } from "react";
import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { ChevronDown, ChevronUp } from "lucide-react";

export default function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <SectionWrapper number="14" title="Frequently Asked Questions" subtitle="Common questions about this appraisal, answered by your appraiser">
      <div className="space-y-2">
        {reportData.faq.map((item, i) => (
          <div key={i} className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
            <button
              className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-[#F8F6F1] transition-colors"
              onClick={() => setOpen(open === i ? null : i)}
            >
              <span className="font-semibold text-sm text-[#1A2F8A] pr-4">{item.q}</span>
              {open === i
                ? <ChevronUp className="w-4 h-4 text-[#29ABE2] shrink-0" />
                : <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" />
              }
            </button>
            {open === i && (
              <div className="px-5 pb-4 border-t border-border/40">
                <p className="text-sm text-muted-foreground leading-relaxed pt-3" style={{ fontFamily: "'Source Serif 4', serif" }}>
                  {item.a}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 bg-[#1A2F8A]/5 border border-[#1A2F8A]/15 rounded-xl p-4 text-center">
        <p className="text-sm text-muted-foreground">
          Have a question not answered here? Contact your appraiser directly at{" "}
          <a href={`mailto:${reportData.appraiser.email}`} className="text-[#29ABE2] hover:underline font-medium">
            {reportData.appraiser.email}
          </a>{" "}
          or{" "}
          <a href={`tel:${reportData.appraiser.phone}`} className="text-[#29ABE2] hover:underline font-medium">
            {reportData.appraiser.phone}
          </a>
        </p>
      </div>
    </SectionWrapper>
  );
}
