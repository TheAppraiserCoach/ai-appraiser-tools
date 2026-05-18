import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { MapView } from "@/components/Map";

const { neighborhood: nbhd, subject } = reportData;

export default function NeighborhoodSection() {
  return (
    <SectionWrapper number="05" title="Neighborhood" subtitle="Market area characteristics, boundaries, and location analysis">
      {/* Aerial photo */}
      <div className="rounded-xl overflow-hidden shadow-sm mb-5" style={{ height: "260px" }}>
        <img
          src="https://d2xsxph8kpxj0f.cloudfront.net/310419663030321591/f5bCTQ69Qyxxa5qdGUj9rt/neighborhood-aerial-BrArTzqGwqE9pELBso8UuJ.webp"
          alt="Neighborhood aerial view"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Key stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        {[
          { label: "Location Type", value: nbhd.location },
          { label: "Built-Up", value: nbhd.builtUp },
          { label: "Growth Rate", value: nbhd.growthRate },
          { label: "Marketing Time", value: nbhd.marketingTime },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-lg border border-border shadow-sm p-3 text-center">
            <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">{item.label}</div>
            <div className="text-[#1A2F8A] font-semibold text-sm">{item.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        {/* Boundaries */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-4">
          <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Neighborhood Boundaries</h3>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(nbhd.boundaries).map(([dir, val]) => (
              <div key={dir} className="bg-[#1A2F8A]/5 rounded-lg p-2 text-center">
                <div className="text-[#29ABE2] text-xs font-semibold uppercase">{dir}</div>
                <div className="text-sm font-medium mt-0.5">{val}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Land use */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-4">
          <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Land Use Mix</h3>
          <div className="space-y-2">
            {[
              { label: "Single Family Residential", pct: nbhd.oneUnitPct },
              { label: "Commercial", pct: nbhd.commercialPct },
              { label: "Vacant Land", pct: nbhd.vacantPct },
              { label: "Other", pct: nbhd.otherPct },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">{item.label}</span>
                  <span className="font-mono font-semibold text-[#1A2F8A]">{item.pct}%</span>
                </div>
                <div className="h-1.5 bg-border rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#29ABE2] rounded-full transition-all duration-1000"
                    style={{ width: `${item.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-border/40 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">Price Range: </span>
              <span className="font-mono font-semibold text-[#1A2F8A]">${(nbhd.priceRange.low / 1000).toFixed(0)}K–${(nbhd.priceRange.high / 1000).toFixed(0)}K</span>
            </div>
            <div>
              <span className="text-muted-foreground">Predominant: </span>
              <span className="font-mono font-semibold text-[#1A2F8A]">${(nbhd.priceRange.predominant / 1000).toFixed(0)}K</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Map */}
      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden mb-5">
        <div className="bg-[#1A2F8A] px-4 py-2.5 flex items-center gap-2">
          <span className="text-white font-semibold text-sm">Interactive Location Map</span>
          <span className="text-white/50 text-xs ml-auto">Jefferson County, Idaho</span>
        </div>
        <div style={{ height: "320px" }}>
          <MapView
            onMapReady={(map) => {
              const subjectPos = { lat: subject.lat, lng: subject.lng };
              map.setCenter(subjectPos);
              map.setZoom(13);

              // Subject marker
              new google.maps.Marker({
                position: subjectPos,
                map,
                title: `Subject: ${subject.address}`,
                icon: {
                  path: google.maps.SymbolPath.CIRCLE,
                  scale: 10,
                  fillColor: "#1A2F8A",
                  fillOpacity: 1,
                  strokeColor: "#29ABE2",
                  strokeWeight: 3,
                },
              });

              // Comparable markers
              const compPositions = [
                { lat: 43.7421, lng: -111.9485, label: "1" },
                { lat: 43.7521, lng: -111.9385, label: "2" },
                { lat: 43.7321, lng: -111.9285, label: "3" },
                { lat: 43.7421, lng: -111.9485, label: "4" },
                { lat: 43.7621, lng: -111.9185, label: "5" },
                { lat: 43.7521, lng: -111.9285, label: "6" },
              ];

              compPositions.forEach((pos) => {
                new google.maps.Marker({
                  position: { lat: pos.lat, lng: pos.lng },
                  map,
                  label: { text: pos.label, color: "white", fontWeight: "bold", fontSize: "11px" },
                  icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: "#29ABE2",
                    fillOpacity: 0.9,
                    strokeColor: "#fff",
                    strokeWeight: 2,
                  },
                });
              });
            }}
          />
        </div>
        <div className="px-4 py-2 bg-[#F8F6F1] border-t border-border flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#1A2F8A] border-2 border-[#29ABE2] inline-block" />
            Subject Property
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#29ABE2] inline-block" />
            Comparable Sales
          </span>
        </div>
      </div>

      {/* Narrative */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-4">
        <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3">Neighborhood Description</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{nbhd.description}</p>
      </div>
    </SectionWrapper>
  );
}
