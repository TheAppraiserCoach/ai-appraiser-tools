import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { CheckCircle2, Mail, Phone, Calendar, FileText } from "lucide-react";

const timeline = [
  { date: "April 17, 2026", label: "Order Placed", desc: "Engagement letter issued and signed", done: true },
  { date: "April 17, 2026", label: "Order Confirmed", desc: "Client acknowledged via email", done: true },
  { date: "April 22, 2026", label: "Property Inspection", desc: "Interior & exterior inspection completed (12PM–4PM)", done: true },
  { date: "April 22, 2026", label: "Payment Received", desc: "$900.00 money order collected at inspection", done: true },
  { date: "April 24, 2026", label: "Report Signed", desc: "Appraiser signed and certified the report", done: true },
  { date: "April 28, 2026", label: "Report Delivered", desc: "Interactive report delivered to client", done: true },
];

export default function EngagementSection() {
  const e = reportData.engagement;

  return (
    <SectionWrapper number="02" title="Engagement & Order" subtitle="Appraisal order details, intended use, and engagement timeline">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Order Details Card */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm uppercase tracking-wider mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#29ABE2]" />
            Order Details
          </h3>
          <div className="space-y-3">
            {[
              { label: "Order Date", value: e.orderDate },
              { label: "Invoice Number", value: e.invoiceNumber, mono: true },
              { label: "Report Type", value: e.reportType },
              { label: "Client Name", value: e.clientName },
              { label: "Property Address", value: e.propertyAddress },
              { label: "Intended Use", value: e.intendedUse },
              { label: "Value Type", value: e.valueType },
              { label: "USPAP Compliant", value: "Yes — Current Edition" },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-start gap-3 py-2 border-b border-border/40 last:border-0">
                <span className="text-muted-foreground text-xs uppercase tracking-wider shrink-0">{row.label}</span>
                <span className={`text-sm text-right font-medium ${row.mono ? "font-mono text-[#1A2F8A]" : ""}`}>{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Contact + Intended Use */}
        <div className="space-y-4">
          {/* Appraiser contact */}
          <div className="bg-[#1A2F8A] rounded-xl p-5 text-white">
            <h3 className="font-semibold text-white/70 text-xs uppercase tracking-wider mb-3">Appraisal Company</h3>
            <div className="font-bold text-lg mb-0.5" style={{ fontFamily: "'Playfair Display', serif" }}>
              {e.appraisalCompany}
            </div>
            <div className="text-white/60 text-sm mb-3">{e.contactName}</div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-sm text-white/80">
                <Phone className="w-3.5 h-3.5 text-[#29ABE2]" />
                {e.phone}
              </div>
              <div className="flex items-center gap-2 text-sm text-white/80">
                <Mail className="w-3.5 h-3.5 text-[#29ABE2]" />
                {e.email}
              </div>
            </div>
          </div>

          {/* Intended use callout */}
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="text-amber-800 text-xs font-semibold uppercase tracking-wider mb-2">⚠ Intended Use Notice</div>
            <p className="text-amber-900 text-sm leading-relaxed">
              This appraisal was prepared <strong>exclusively</strong> for the purpose of: <em>"{e.intendedUse}."</em>
            </p>
            <p className="text-amber-700 text-xs mt-2">
              The intended user is {e.clientName}. This report may not be used for mortgage lending, tax appeals, or any other purpose without written consent from the appraiser.
            </p>
          </div>

          {/* Delivery info */}
          <div className="bg-white rounded-xl border border-border p-4">
            <div className="text-muted-foreground text-xs uppercase tracking-wider mb-2">Report Delivery</div>
            <div className="flex items-center gap-2 text-sm">
              <Mail className="w-3.5 h-3.5 text-[#29ABE2]" />
              <span className="font-mono text-[#1A2F8A]">{e.deliveryEmail}</span>
            </div>
            <div className="flex items-center gap-2 text-sm mt-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#29ABE2]" />
              <span className="text-muted-foreground">Delivered by {reportData.deliveryDate}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="mt-5 bg-white rounded-xl border border-border shadow-sm p-5">
        <h3 className="font-semibold text-[#1A2F8A] text-sm uppercase tracking-wider mb-4">Engagement Timeline</h3>
        <div className="relative">
          <div className="absolute left-[18px] top-0 bottom-0 w-px bg-[#29ABE2]/20" />
          <div className="space-y-4">
            {timeline.map((step, i) => (
              <div key={i} className="flex items-start gap-4 relative">
                <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 ${step.done ? "bg-[#29ABE2]" : "bg-border"}`}>
                  <CheckCircle2 className={`w-4 h-4 ${step.done ? "text-white" : "text-muted-foreground"}`} />
                </div>
                <div className="flex-1 pb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-foreground">{step.label}</span>
                    <span className="text-xs text-muted-foreground font-mono">{step.date}</span>
                  </div>
                  <p className="text-muted-foreground text-xs mt-0.5">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </SectionWrapper>
  );
}
