import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { CheckCircle2, DollarSign, FileText, CreditCard } from "lucide-react";

export default function PaymentSection() {
  const e = reportData.engagement;

  return (
    <SectionWrapper number="03" title="Payment Confirmation" subtitle="Fee, payment method, and receipt of funds">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        {/* Paid badge */}
        <div className="sm:col-span-1 bg-emerald-50 border border-emerald-200 rounded-xl p-5 flex flex-col items-center justify-center text-center">
          <div className="w-14 h-14 rounded-full bg-emerald-100 border-2 border-emerald-400 flex items-center justify-center mb-3">
            <CheckCircle2 className="w-7 h-7 text-emerald-600" />
          </div>
          <div className="text-emerald-800 font-bold text-2xl font-mono">${e.paymentAmount.toLocaleString()}.00</div>
          <div className="text-emerald-700 font-semibold text-sm mt-1">PAID IN FULL</div>
          <div className="text-emerald-600 text-xs mt-1">{e.paymentDate}</div>
        </div>

        {/* Payment details */}
        <div className="sm:col-span-2 bg-white rounded-xl border border-border shadow-sm p-5">
          <h3 className="font-semibold text-[#1A2F8A] text-sm uppercase tracking-wider mb-4 flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-[#29ABE2]" />
            Payment Details
          </h3>
          <div className="space-y-3">
            {[
              { label: "Invoice Number", value: e.invoiceNumber, mono: true },
              { label: "Appraisal Fee", value: `$${e.fee.toLocaleString()}.00`, mono: true },
              { label: "Payment Method", value: "Money Order (ICCU #750078)" },
              { label: "Payment Date", value: e.paymentDate },
              { label: "Payable To", value: e.appraisalCompany },
              { label: "Payment Status", value: "✓ Paid — Report Released" },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center py-2 border-b border-border/40 last:border-0">
                <span className="text-muted-foreground text-xs uppercase tracking-wider">{row.label}</span>
                <span className={`text-sm font-medium ${row.mono ? "font-mono text-[#1A2F8A]" : ""}`}>{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Invoice summary */}
      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="bg-[#1A2F8A] px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#29ABE2]" />
            <span className="text-white font-semibold text-sm">Invoice Summary</span>
          </div>
          <span className="text-white/60 text-xs font-mono">{e.invoiceNumber}</span>
        </div>
        <div className="p-5">
          <div className="flex justify-between items-center py-2 border-b border-border/40">
            <span className="text-sm">General Purpose Appraisal Report (GPAR)</span>
            <span className="font-mono font-semibold text-[#1A2F8A]">$900.00</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-border/40">
            <span className="text-sm text-muted-foreground">Property: {e.propertyAddress}</span>
            <span className="text-muted-foreground text-sm">—</span>
          </div>
          <div className="flex justify-between items-center py-3 mt-1">
            <span className="font-bold text-[#1A2F8A]">TOTAL PAID</span>
            <span className="font-mono font-bold text-xl text-[#1A2F8A]">$900.00</span>
          </div>
        </div>
      </div>

      <p className="text-muted-foreground text-xs mt-3 text-center">
        Payment collected at time of inspection per engagement letter terms. Report released upon receipt of payment.
      </p>
    </SectionWrapper>
  );
}
