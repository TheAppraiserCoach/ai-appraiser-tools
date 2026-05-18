import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";

const { site, subject, improvements } = reportData;

export default function SiteSection() {
  return (
    <SectionWrapper number="06" title="Site & GIS" subtitle="Lot characteristics, utilities, flood zone, and parcel data">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        <div className="bg-white rounded-xl border border-border shadow-sm p-4">
          <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Site Characteristics</h3>
          <div className="space-y-2">
            {[
              { label: "Site Area", value: site.siteArea },
              { label: "Site Area (SF)", value: `${site.siteAreaSF.toLocaleString()} sf` },
              { label: "Shape", value: site.shape },
              { label: "Topography", value: site.topography },
              { label: "Street", value: site.street },
              { label: "Drainage", value: site.drainage },
              { label: "View", value: "Residential — No adverse view" },
              { label: "Lot Type", value: "Inside Lot" },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center py-1.5 border-b border-border/30 last:border-0">
                <span className="text-muted-foreground text-xs">{row.label}</span>
                <span className="text-sm font-medium font-mono">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-border shadow-sm p-4">
            <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Utilities</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: "Water", value: improvements.utilities.water },
                { label: "Sewer", value: improvements.utilities.sewer },
                { label: "Gas", value: "Public" },
                { label: "Electric", value: "Public" },
              ].map((item) => (
                <div key={item.label} className="bg-[#1A2F8A]/5 rounded-lg p-2">
                  <div className="text-[#29ABE2] text-xs font-semibold">{item.label}</div>
                  <div className="text-sm font-medium mt-0.5">{item.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <h3 className="font-semibold text-emerald-800 text-xs uppercase tracking-wider mb-2">FEMA Flood Zone</h3>
            <div className="text-3xl font-bold font-mono text-emerald-700 mb-1">{improvements.floodZone}</div>
            <p className="text-emerald-700 text-xs">Outside Special Flood Hazard Area — flood insurance not required</p>
            <div className="mt-2 text-emerald-600 text-xs font-mono">
              Map #{improvements.floodMapNo} · {improvements.floodMapDate}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-border shadow-sm p-4">
            <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-2">Zoning</h3>
            <div className="text-sm font-semibold text-[#1A2F8A]">{subject.zoning.split(" ")[0]}</div>
            <p className="text-xs text-muted-foreground mt-1">{subject.zoning}</p>
            <div className="mt-2 inline-flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 rounded-full px-2.5 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-emerald-700 text-xs font-medium">Legal Conforming Use</span>
            </div>
          </div>
        </div>
      </div>

      {/* Parcel info */}
      <div className="bg-[#1A2F8A] rounded-xl p-4 text-white">
        <h3 className="text-white/60 text-xs uppercase tracking-wider mb-3">Jefferson County Assessor Record</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Parcel Number", value: subject.parcelNumber },
            { label: "County", value: subject.county },
            { label: "Tax Year", value: subject.taxYear },
            { label: "Annual Taxes", value: `$${subject.annualTaxes.toLocaleString()}` },
          ].map((item) => (
            <div key={item.label}>
              <div className="text-white/40 text-xs mb-0.5">{item.label}</div>
              <div className="text-white font-mono font-semibold text-sm">{item.value}</div>
            </div>
          ))}
        </div>
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="text-white/40 text-xs mb-0.5">Legal Description</div>
          <div className="text-white/80 text-xs font-mono">{subject.legalDescription}</div>
        </div>
      </div>
    </SectionWrapper>
  );
}
