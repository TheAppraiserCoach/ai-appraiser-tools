import { useState } from "react";
import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { X, ZoomIn } from "lucide-react";

// Real property photos extracted from appraisal work file (4067 E 518 N, Rigby ID)
const photos = [
  {
    url: "/manus-storage/photo-front_06a509ce.png",
    caption: "Subject Front — 4067 E 518 N",
    category: "Exterior",
  },
  {
    url: "/manus-storage/photo-rear_5a268e74.png",
    caption: "Subject Rear — Covered Porch & Yard",
    category: "Exterior",
  },
  {
    url: "/manus-storage/photo-street_ef45ae83.png",
    caption: "Subject Street — Driveway Approach",
    category: "Exterior",
  },
  {
    url: "/manus-storage/photo-side1_8024aa90.png",
    caption: "Side Exterior — Stone & Siding Detail",
    category: "Exterior",
  },
  {
    url: "/manus-storage/photo-kitchen_fbecac82.png",
    caption: "Kitchen — Granite Countertops, Stainless Appliances",
    category: "Interior",
  },
  {
    url: "/manus-storage/photo-living_6e2ead8e.png",
    caption: "Living Room — Vaulted Ceilings, Fireplace",
    category: "Interior",
  },
  {
    url: "/manus-storage/photo-primary-bed_c4c8ecd2.png",
    caption: "Primary Bedroom",
    category: "Interior",
  },
  {
    url: "/manus-storage/photo-primary-bath_7470040b.png",
    caption: "Primary Bathroom — Granite Vanity",
    category: "Interior",
  },
  {
    url: "/manus-storage/photo-family_b8fadf4d.png",
    caption: "Basement Family Room — Fully Finished",
    category: "Interior",
  },
  {
    url: "/manus-storage/photo-garage_ee79ab2c.png",
    caption: "3-Car Attached Garage — Interior",
    category: "Exterior",
  },
];

const categories = ["All", "Exterior", "Interior", "Neighborhood"];

export default function PhotoSection() {
  const [filter, setFilter] = useState("All");
  const [lightbox, setLightbox] = useState<number | null>(null);

  const filtered = filter === "All" ? photos : photos.filter((p) => p.category === filter);

  return (
    <SectionWrapper number="12" title="Photo Gallery" subtitle="Subject property photographs taken at time of inspection — April 22, 2026">
      {/* Filter tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              filter === cat
                ? "bg-[#1A2F8A] text-white"
                : "bg-white border border-border text-muted-foreground hover:border-[#29ABE2] hover:text-[#1A2F8A]"
            }`}
          >
            {cat} {cat === "All" ? `(${photos.length})` : `(${photos.filter((p) => p.category === cat).length})`}
          </button>
        ))}
      </div>

      {/* Photo grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {filtered.map((photo, i) => {
          const originalIndex = photos.indexOf(photo);
          return (
            <div
              key={i}
              className="relative group rounded-xl overflow-hidden cursor-pointer shadow-sm border border-border"
              style={{ aspectRatio: "4/3" }}
              onClick={() => setLightbox(originalIndex)}
            >
              <img
                src={photo.url}
                alt={photo.caption}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-[#1A2F8A]/0 group-hover:bg-[#1A2F8A]/40 transition-all duration-300 flex items-center justify-center">
                <ZoomIn className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                <p className="text-white text-xs leading-tight">{photo.caption}</p>
                <span className="text-[#29ABE2] text-xs">{photo.category}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox */}
      {lightbox !== null && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setLightbox(null)}
        >
          <button
            className="absolute top-4 right-4 text-white/70 hover:text-white"
            onClick={() => setLightbox(null)}
          >
            <X className="w-6 h-6" />
          </button>
          <div className="max-w-3xl w-full" onClick={(e) => e.stopPropagation()}>
            <img
              src={photos[lightbox].url}
              alt={photos[lightbox].caption}
              className="w-full rounded-xl shadow-2xl"
            />
            <p className="text-white text-center mt-3 text-sm">{photos[lightbox].caption}</p>
            <div className="flex justify-center gap-2 mt-3">
              {lightbox > 0 && (
                <button
                  className="text-white/60 hover:text-white text-sm px-3 py-1 border border-white/20 rounded-lg"
                  onClick={() => setLightbox(lightbox - 1)}
                >
                  ← Previous
                </button>
              )}
              <span className="text-white/40 text-sm px-3 py-1">{lightbox + 1} / {photos.length}</span>
              {lightbox < photos.length - 1 && (
                <button
                  className="text-white/60 hover:text-white text-sm px-3 py-1 border border-white/20 rounded-lg"
                  onClick={() => setLightbox(lightbox + 1)}
                >
                  Next →
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <p className="text-muted-foreground text-xs text-center mt-3">
        Photos taken by {reportData.appraiser.name} on {reportData.engagement.inspectionDate}. Click any photo to enlarge.
      </p>
    </SectionWrapper>
  );
}

