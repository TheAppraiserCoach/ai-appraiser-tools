import SectionWrapper from "@/components/SectionWrapper";
import { reportData } from "@/lib/appraisalData";
import { Phone, Mail, Globe, Award, Shield } from "lucide-react";

const { appraiser } = reportData;

export default function AppraiserSection() {
  return (
    <SectionWrapper number="15" title="Appraiser Profile" subtitle="Credentials, certification, and contact information">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Profile card */}
        <div className="lg:col-span-1">
          <div className="bg-[#1A2F8A] rounded-xl p-6 text-white text-center">
            {/* Mountain logo */}
            <div className="flex justify-center mb-4">
              <svg width="56" height="36" viewBox="0 0 64 40" fill="none">
                <path d="M32 2L48 32H16L32 2Z" fill="#29ABE2" opacity="0.9"/>
                <path d="M50 10L62 32H38L50 10Z" fill="#29ABE2" opacity="0.6"/>
                <path d="M14 14L26 32H2L14 14Z" fill="#29ABE2" opacity="0.6"/>
              </svg>
            </div>
            <div className="font-bold text-xl mb-0.5" style={{ fontFamily: "'Playfair Display', serif" }}>
              {appraiser.name}
            </div>
            <div className="text-[#29ABE2] text-sm mb-1">{appraiser.designation}</div>
            <div className="text-white/60 text-sm mb-4">{appraiser.company}</div>

            <div className="space-y-2 text-left">
              <a href={`tel:${appraiser.phone}`} className="flex items-center gap-2 text-white/80 hover:text-white text-sm transition-colors">
                <Phone className="w-3.5 h-3.5 text-[#29ABE2]" />
                {appraiser.phone}
              </a>
              <a href={`mailto:${appraiser.email}`} className="flex items-center gap-2 text-white/80 hover:text-white text-sm transition-colors">
                <Mail className="w-3.5 h-3.5 text-[#29ABE2]" />
                {appraiser.email}
              </a>
              <a href={`https://${appraiser.website}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-white/80 hover:text-white text-sm transition-colors">
                <Globe className="w-3.5 h-3.5 text-[#29ABE2]" />
                {appraiser.website}
              </a>
            </div>
          </div>
        </div>

        {/* Credentials */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl border border-border shadow-sm p-5">
            <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-4 flex items-center gap-2">
              <Award className="w-4 h-4 text-[#29ABE2]" />
              License & Credentials
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "License Number", value: appraiser.licenseNumber },
                { label: "License State", value: appraiser.licenseState },
                { label: "Designation", value: appraiser.designation },
                { label: "License Expires", value: appraiser.licenseExpiration },
                { label: "Years Experience", value: `${appraiser.yearsExperience}+ years` },
                { label: "Signature Date", value: appraiser.signatureDate },
              ].map((item) => (
                <div key={item.label} className="bg-[#F8F6F1] rounded-lg p-3">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-0.5">{item.label}</div>
                  <div className="font-mono font-semibold text-sm text-[#1A2F8A]">{item.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-border shadow-sm p-5">
            <h3 className="font-semibold text-[#1A2F8A] text-xs uppercase tracking-wider mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#29ABE2]" />
              USPAP Compliance Statement
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              This appraisal was prepared in conformance with the Uniform Standards of Professional Appraisal Practice (USPAP), current edition, and the requirements of the Appraisal Institute. The appraiser has complied with the competency provision and the disclosure requirements of USPAP.
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-emerald-600" />
              <span className="text-emerald-800 font-semibold text-sm">Idaho Certified Residential Appraiser</span>
            </div>
            <p className="text-emerald-700 text-xs">
              Licensed by the Idaho Real Estate Appraiser Board. License #{appraiser.licenseNumber} is active and in good standing through {appraiser.licenseExpiration}.
            </p>
          </div>
        </div>
      </div>

      {/* Report summary footer */}
      <div className="mt-5 bg-[#1A2F8A] rounded-xl p-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          {[
            { label: "File Number", value: reportData.fileNo },
            { label: "Final Value", value: `$${reportData.finalValue.toLocaleString()}` },
            { label: "Effective Date", value: reportData.effectiveDate },
            { label: "Report Expires", value: reportData.expirationDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) },
          ].map((item) => (
            <div key={item.label}>
              <div className="text-white/40 text-xs uppercase tracking-wider mb-1">{item.label}</div>
              <div className="text-white font-mono font-semibold text-sm">{item.value}</div>
            </div>
          ))}
        </div>
      </div>
    </SectionWrapper>
  );
}
