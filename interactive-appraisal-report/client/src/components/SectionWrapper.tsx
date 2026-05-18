import React from "react";

interface SectionWrapperProps {
  number: string;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

export default function SectionWrapper({ number, title, subtitle, children, className = "" }: SectionWrapperProps) {
  return (
    <section className={`section-fade-in ${className}`}>
      {/* Section header */}
      <div className="flex items-start gap-4 mb-6">
        <div className="shrink-0 w-10 h-10 rounded bg-[#1A2F8A] flex items-center justify-center">
          <span className="text-[#29ABE2] text-xs font-mono font-semibold">{number}</span>
        </div>
        <div className="border-b border-[#1A2F8A]/20 pb-3 flex-1">
          <h2 className="section-header text-xl">{title}</h2>
          {subtitle && <p className="text-muted-foreground text-sm mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}
