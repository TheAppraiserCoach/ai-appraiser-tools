import { useEffect, useState } from "react";
import { reportData } from "@/lib/appraisalData";
import { Calendar, Home, FileCheck, Clock } from "lucide-react";

export default function CoverSection() {
  const [daysLeft, setDaysLeft] = useState(0);
  const [countedValue, setCountedValue] = useState(0);

  useEffect(() => {
    const now = new Date();
    const diff = reportData.expirationDate.getTime() - now.getTime();
    const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    setDaysLeft(days);

    // Count-up animation for final value
    const target = reportData.finalValue;
    const duration = 1200;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCountedValue(target);
        clearInterval(timer);
      } else {
        setCountedValue(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="section-fade-in">
      {/* Hero image + value card */}
      <div className="relative rounded-xl overflow-hidden shadow-xl mb-6" style={{ height: "340px" }}>
        <img
          src="/manus-storage/subject-front_43c0cbad.png"
          alt="Subject Property"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#1A2F8A]/90 via-[#1A2F8A]/30 to-transparent" />

        {/* Expiration badge */}
        <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-black/40 backdrop-blur-sm border border-white/20 rounded-full px-3 py-1.5">
          <Clock className="w-3.5 h-3.5 text-[#29ABE2]" />
          <span className="text-white text-xs font-medium">{daysLeft} days remaining</span>
        </div>

        {/* Confidential badge */}
        <div className="absolute top-4 left-4 bg-[#1A2F8A]/80 backdrop-blur-sm border border-[#29ABE2]/30 rounded-full px-3 py-1.5">
          <span className="text-[#29ABE2] text-xs font-semibold uppercase tracking-wider">Confidential</span>
        </div>

        {/* Value overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6">
          <div className="flex items-end justify-between">
            <div>
              <div className="text-white/60 text-sm mb-1">Opinion of Market Value</div>
              <div className="value-hero text-white text-5xl font-semibold" style={{ fontFamily: "'IBM Plex Mono', monospace" }}>
                ${countedValue.toLocaleString()}
              </div>
              <div className="text-white/70 text-sm mt-1">
                As of {reportData.effectiveDate}
              </div>
            </div>
            <div className="text-right hidden sm:block">
              <div className="text-white/50 text-xs">Appraised by</div>
              <div className="text-white font-semibold text-sm">{reportData.appraiser.name}</div>
              <div className="text-[#29ABE2] text-xs">{reportData.appraiser.company}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Property address */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-5 mb-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded bg-[#1A2F8A]/10 flex items-center justify-center shrink-0 mt-0.5">
            <Home className="w-4 h-4 text-[#1A2F8A]" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-[#1A2F8A]" style={{ fontFamily: "'Playfair Display', serif" }}>
              {reportData.subject.address}
            </h1>
            <p className="text-muted-foreground text-sm">
              {reportData.subject.city}, {reportData.subject.state} {reportData.subject.zip} · {reportData.subject.county} County
            </p>
            <p className="text-xs text-muted-foreground/70 mt-1 font-mono">
              {reportData.subject.legalDescription}
            </p>
          </div>
        </div>
      </div>

      {/* Key facts grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        {[
          { label: "File Number", value: reportData.fileNo, mono: true },
          { label: "Effective Date", value: reportData.effectiveDate },
          { label: "Report Type", value: "GPAR — Full Report" },
          { label: "Intended Use", value: "Pre-Nuptial Agreement" },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-lg border border-border p-3 shadow-sm">
            <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">{item.label}</div>
            <div className={`text-sm font-semibold text-foreground ${item.mono ? "font-mono" : ""}`}>
              {item.value}
            </div>
          </div>
        ))}
      </div>

      {/* Property quick stats */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
        {[
          { label: "Style", value: reportData.improvements.style },
          { label: "GLA", value: `${reportData.improvements.grossLivingArea.toLocaleString()} sf` },
          { label: "Bed/Bath", value: `${reportData.improvements.bedrooms}/${reportData.improvements.bathrooms}` },
          { label: "Garage", value: reportData.improvements.garageType },
          { label: "Lot Size", value: reportData.site.siteArea },
          { label: "Year Built", value: String(reportData.improvements.yearBuilt) },
        ].map((item) => (
          <div key={item.label} className="bg-[#1A2F8A]/5 rounded-lg p-3 text-center border border-[#1A2F8A]/10">
            <div className="text-[#1A2F8A] text-xs uppercase tracking-wider mb-1">{item.label}</div>
            <div className="text-[#1A2F8A] font-semibold text-sm font-mono">{item.value}</div>
          </div>
        ))}
      </div>

      {/* Expiration notice */}
      <div className="mt-4 flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
        <Calendar className="w-4 h-4 text-amber-600 shrink-0" />
        <p className="text-amber-800 text-xs">
          <strong>Report Expiration:</strong> This interactive report is accessible until{" "}
          <strong>{reportData.expirationDate.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</strong>
          {" "}({daysLeft} days remaining). The appraisal reflects market conditions as of {reportData.effectiveDate}.
        </p>
      </div>
    </section>
  );
}
