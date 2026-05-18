import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";

const { improvements: imp, subject } = reportData;

const detailGroups = [
  {
    title: "General Description",
    items: [
      { label: "Style", value: imp.style },
      { label: "Year Built", value: String(imp.yearBuilt) },
      { label: "Actual Age", value: `${imp.actualAge} years` },
      { label: "Effective Age", value: `${imp.effectiveAge} years` },
      { label: "Stories", value: String(imp.stories) },
      { label: "Quality", value: imp.quality },
      { label: "Condition", value: imp.condition },
    ],
  },
  {
    title: "Size & Layout",
    items: [
      { label: "Gross Living Area", value: `${imp.grossLivingArea.toLocaleString()} sf` },
      { label: "Basement Area", value: `${imp.basementArea.toLocaleString()} sf` },
      { label: "Basement Finished", value: `${imp.basementFinished.toLocaleString()} sf` },
      { label: "Garage", value: `${imp.garageArea} sf (${imp.garageType})` },
      { label: "Total Rooms", value: String(imp.totalRooms) },
      { label: "Bedrooms", value: String(imp.bedrooms) },
      { label: "Bathrooms", value: imp.bathrooms },
    ],
  },
  {
    title: "Construction",
    items: [
      { label: "Foundation", value: imp.foundation },
      { label: "Exterior Walls", value: imp.exteriorWalls },
      { label: "Roof Surface", value: imp.roofSurface },
      { label: "Heating", value: imp.heating },
      { label: "Cooling", value: imp.cooling },
    ],
  },
  {
    title: "Utilities & Systems",
    items: [
      { label: "Water", value: imp.utilities.water },
      { label: "Sewer", value: imp.utilities.sewer },
      { label: "Gas", value: imp.utilities.gas },
      { label: "Electricity", value: imp.utilities.electricity },
      { label: "FEMA Flood Zone", value: imp.floodZone },
      { label: "Flood Map #", value: imp.floodMapNo },
    ],
  },
];

export default function SubjectSection() {
  return (
    <SectionWrapper number="04" title="Subject Property" subtitle="Physical characteristics, construction details, and property description">
      {/* Assessor info */}
      <div className="bg-[#1A2F8A]/5 border border-[#1A2F8A]/15 rounded-xl p-4 mb-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wider">Parcel Number</div>
            <div className="font-mono text-sm font-semibold text-[#1A2F8A] mt-0.5">{subject.parcelNumber}</div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wider">Tax Year</div>
            <div className="font-mono text-sm font-semibold text-[#1A2F8A] mt-0.5">{subject.taxYear}</div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wider">Annual Taxes</div>
            <div className="font-mono text-sm font-semibold text-[#1A2F8A] mt-0.5">${subject.annualTaxes.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-muted-foreground text-xs uppercase tracking-wider">Zoning</div>
            <div className="text-sm font-semibold text-[#1A2F8A] mt-0.5">{subject.zoning.split(" ")[0]}</div>
          </div>
        </div>
      </div>

      {/* Detail groups */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        {detailGroups.map((group) => (
          <div key={group.title} className="bg-white rounded-xl border border-border shadow-sm p-4">
            <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3 pb-2 border-b border-border/50">
              {group.title}
            </h3>
            <div className="space-y-2">
              {group.items.map((item) => (
                <div key={item.label} className="flex justify-between items-center">
                  <span className="text-muted-foreground text-xs">{item.label}</span>
                  <span className="text-sm font-medium font-mono text-foreground">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Amenities */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-4 mb-4">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Amenities & Features</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {imp.amenities.map((a) => (
            <span key={a} className="bg-[#29ABE2]/10 border border-[#29ABE2]/30 text-[#1A2F8A] text-xs px-3 py-1 rounded-full font-medium">
              {a}
            </span>
          ))}
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">{imp.additionalFeatures}</p>
      </div>

      {/* Condition note */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-4">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-2">Condition Summary</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          The subject is a single family home in <strong>good condition (C2)</strong>. No significant repairs or inadequacies were noted. Physical depreciation is noted for normal age wear. No functional or external obsolescence is warranted. The subject has vaulted ceilings, granite countertops, custom cabinets, and stainless steel appliances.
        </p>
      </div>
    </SectionWrapper>
  );
}
