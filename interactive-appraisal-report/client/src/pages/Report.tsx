import { useState, useEffect, useRef } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";
import { reportData } from "@/lib/appraisalData";
import {
  Home, MapPin, BarChart2, DollarSign, FileText, Camera, HelpCircle,
  User, ClipboardList, CreditCard, Map, BookOpen, TrendingUp, Building2,
  Scale, LogOut, Menu, X, ChevronRight, Clock, Printer
} from "lucide-react";

// Section components
import CoverSection from "@/components/sections/CoverSection";
import EngagementSection from "@/components/sections/EngagementSection";
import PaymentSection from "@/components/sections/PaymentSection";
import SubjectSection from "@/components/sections/SubjectSection";
import NeighborhoodSection from "@/components/sections/NeighborhoodSection";
import SiteSection from "@/components/sections/SiteSection";
import MarketSection from "@/components/sections/MarketSection";
import SalesCompSection from "@/components/sections/SalesCompSection";
import CostApproachSection from "@/components/sections/CostApproachSection";
import ReconciliationSection from "@/components/sections/ReconciliationSection";
import NarrativeSection from "@/components/sections/NarrativeSection";
import PhotoSection from "@/components/sections/PhotoSection";
import SketchSection from "@/components/sections/SketchSection";
import FAQSection from "@/components/sections/FAQSection";
import AppraiserSection from "@/components/sections/AppraiserSection";

const navItems = [
  { id: "cover", label: "Value Summary", icon: Home, section: 1 },
  { id: "engagement", label: "Engagement & Order", icon: ClipboardList, section: 2 },
  { id: "payment", label: "Payment Confirmation", icon: CreditCard, section: 3 },
  { id: "subject", label: "Subject Property", icon: Building2, section: 4 },
  { id: "neighborhood", label: "Neighborhood", icon: MapPin, section: 5 },
  { id: "site", label: "Site & GIS", icon: Map, section: 6 },
  { id: "market", label: "Market Analysis", icon: TrendingUp, section: 7 },
  { id: "salescomp", label: "Sales Comparison", icon: BarChart2, section: 8 },
  { id: "cost", label: "Cost Approach", icon: DollarSign, section: 9 },
  { id: "reconciliation", label: "Reconciliation", icon: Scale, section: 10 },
  { id: "narrative", label: "Narrative & Addenda", icon: BookOpen, section: 11 },
  { id: "photos", label: "Photo Gallery", icon: Camera, section: 12 },
  { id: "sketch", label: "Building Sketch", icon: FileText, section: 13 },
  { id: "faq", label: "FAQ", icon: HelpCircle, section: 14 },
  { id: "appraiser", label: "Appraiser Profile", icon: User, section: 15 },
];

export default function Report() {
  const { isAuthenticated, logout } = useAuth();
  const [, setLocation] = useLocation();
  const [activeSection, setActiveSection] = useState("cover");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [daysLeft, setDaysLeft] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLocation("/");
    }
  }, [isAuthenticated, setLocation]);

  useEffect(() => {
    const now = new Date();
    const diff = reportData.expirationDate.getTime() - now.getTime();
    const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    setDaysLeft(days);
  }, []);

  const handleLogout = () => {
    logout();
    setLocation("/");
  };

  const handlePrint = () => {
    window.print();
  };

  const scrollToSection = (id: string) => {
    setActiveSection(id);
    setMobileNavOpen(false);
    const el = document.getElementById(`section-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  // Scroll spy
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace("section-", "");
            setActiveSection(id);
          }
        });
      },
      { threshold: 0.2, rootMargin: "-80px 0px -60% 0px" }
    );

    navItems.forEach(({ id }) => {
      const el = document.getElementById(`section-${id}`);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen flex flex-col bg-[#F8F6F1]">
      {/* Top Header */}
      <header className="sticky top-0 z-50 bg-[#1A2F8A] border-b border-[#1A2F8A]/80 shadow-lg">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Logo + Title */}
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden text-white/70 hover:text-white p-1"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
            >
              {mobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2">
              <svg width="28" height="18" viewBox="0 0 64 40" fill="none">
                <path d="M32 2L48 32H16L32 2Z" fill="#29ABE2" opacity="0.9"/>
                <path d="M50 10L62 32H38L50 10Z" fill="#29ABE2" opacity="0.6"/>
                <path d="M14 14L26 32H2L14 14Z" fill="#29ABE2" opacity="0.6"/>
              </svg>
              <div>
                <div className="text-white font-bold text-sm leading-none" style={{ fontFamily: "'Playfair Display', serif" }}>
                  PEAK VALUE APPRAISALS
                </div>
                <div className="text-white/50 text-xs leading-none mt-0.5">
                  {reportData.subject.address}, {reportData.subject.city}, {reportData.subject.state}
                </div>
              </div>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {daysLeft > 0 && (
              <div className="hidden sm:flex items-center gap-1.5 bg-[#29ABE2]/20 border border-[#29ABE2]/30 rounded-full px-3 py-1">
                <Clock className="w-3 h-3 text-[#29ABE2]" />
                <span className="text-[#29ABE2] text-xs font-medium">{daysLeft}d remaining</span>
              </div>
            )}
            <div className="hidden md:block text-right">
              <div className="text-white/40 text-xs">Final Value</div>
              <div className="text-white font-semibold text-sm" style={{ fontFamily: "'IBM Plex Mono', monospace" }}>
                ${reportData.finalValue.toLocaleString()}
              </div>
            </div>
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 bg-[#29ABE2]/20 hover:bg-[#29ABE2]/40 border border-[#29ABE2]/40 text-[#29ABE2] hover:text-white text-xs font-medium px-3 py-1.5 rounded-full transition-all print:hidden"
              title="Save as PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Save PDF</span>
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-white/50 hover:text-white text-xs transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Exit</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigation Rail */}
        <aside
          className={`
            fixed lg:sticky top-[57px] left-0 z-40 h-[calc(100vh-57px)]
            w-64 bg-[#1A2F8A] border-r border-[#29ABE2]/10 overflow-y-auto
            transform transition-transform duration-300 ease-in-out print:hidden
            ${mobileNavOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
        >
          {/* Nav header */}
          <div className="px-4 py-4 border-b border-white/10">
            <div className="text-white/40 text-xs uppercase tracking-widest">Report Sections</div>
            <div className="text-white/60 text-xs mt-1">File No. {reportData.fileNo}</div>
          </div>

          <nav className="py-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={`
                    w-full flex items-center gap-3 px-4 py-2.5 text-left transition-all duration-150
                    ${isActive
                      ? "bg-[#29ABE2]/15 border-l-[3px] border-[#29ABE2] text-white"
                      : "border-l-[3px] border-transparent text-white/50 hover:text-white/80 hover:bg-white/5"
                    }
                  `}
                >
                  <span className={`text-xs font-mono w-4 text-right shrink-0 ${isActive ? "text-[#29ABE2]" : "text-white/25"}`}>
                    {String(item.section).padStart(2, "0")}
                  </span>
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-[#29ABE2]" : ""}`} />
                  <span className="text-xs font-medium truncate">{item.label}</span>
                  {isActive && <ChevronRight className="w-3 h-3 ml-auto text-[#29ABE2] shrink-0" />}
                </button>
              );
            })}
          </nav>

          {/* Nav footer */}
          <div className="px-4 py-4 border-t border-white/10 mt-2">
            <div className="text-white/30 text-xs">Effective Date</div>
            <div className="text-white/60 text-xs mt-0.5">{reportData.effectiveDate}</div>
            <div className="text-white/30 text-xs mt-2">Expires</div>
            <div className="text-white/60 text-xs mt-0.5">
              {reportData.expirationDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
            </div>
          </div>
        </aside>

        {/* Mobile overlay */}
        {mobileNavOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={() => setMobileNavOpen(false)}
          />
        )}

        {/* Main Content */}
        <main ref={contentRef} className="flex-1 overflow-y-auto print:overflow-visible print:w-full">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-12 print:max-w-full print:px-0 print:py-0 print:space-y-0">
            <section id="section-cover"><CoverSection /></section>
            <section id="section-engagement"><EngagementSection /></section>
            <section id="section-payment"><PaymentSection /></section>
            <section id="section-subject"><SubjectSection /></section>
            <section id="section-neighborhood"><NeighborhoodSection /></section>
            <section id="section-site"><SiteSection /></section>
            <section id="section-market"><MarketSection /></section>
            <section id="section-salescomp"><SalesCompSection /></section>
            <section id="section-cost"><CostApproachSection /></section>
            <section id="section-reconciliation"><ReconciliationSection /></section>
            <section id="section-narrative"><NarrativeSection /></section>
            <section id="section-photos"><PhotoSection /></section>
            <section id="section-sketch"><SketchSection /></section>
            <section id="section-faq"><FAQSection /></section>
            <section id="section-appraiser"><AppraiserSection /></section>
          </div>

          {/* Footer */}
          <footer className="border-t border-border/50 bg-white/50 mt-8 py-6 px-6">
            <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <svg width="20" height="13" viewBox="0 0 64 40" fill="none">
                  <path d="M32 2L48 32H16L32 2Z" fill="#1A2F8A"/>
                  <path d="M50 10L62 32H38L50 10Z" fill="#29ABE2" opacity="0.7"/>
                  <path d="M14 14L26 32H2L14 14Z" fill="#29ABE2" opacity="0.7"/>
                </svg>
                <span className="text-xs text-muted-foreground">
                  © 2026 Peak Value Appraisals · File No. {reportData.fileNo}
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                This report is confidential and intended solely for {reportData.engagement.clientName}
              </div>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
