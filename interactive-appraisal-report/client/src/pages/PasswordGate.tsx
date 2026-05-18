import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";
import { reportData } from "@/lib/appraisalData";
import { Lock, AlertCircle, Clock } from "lucide-react";

export default function PasswordGate() {
  const { isAuthenticated, login } = useAuth();
  const [, setLocation] = useLocation();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [shake, setShake] = useState(false);
  const [daysLeft, setDaysLeft] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      setLocation("/report");
    }
  }, [isAuthenticated, setLocation]);

  useEffect(() => {
    const now = new Date();
    const diff = reportData.expirationDate.getTime() - now.getTime();
    const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    setDaysLeft(days);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const success = login(password);
    if (success) {
      setLocation("/report");
    } else {
      setError("Incorrect password. Please contact your appraiser.");
      setShake(true);
      setTimeout(() => setShake(false), 600);
      setPassword("");
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{
        backgroundImage: `url(https://d2xsxph8kpxj0f.cloudfront.net/310419663030321591/f5bCTQ69Qyxxa5qdGUj9rt/password-bg-bZVVyYd5vzuLDDa3aPU9fQ.webp)`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-[#0F1E5A]/80" />

      {/* Content */}
      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex flex-col items-center">
            {/* Mountain SVG icon */}
            <svg width="64" height="40" viewBox="0 0 64 40" fill="none" className="mb-3">
              <path d="M32 2L48 32H16L32 2Z" fill="#29ABE2" opacity="0.9"/>
              <path d="M50 10L62 32H38L50 10Z" fill="#29ABE2" opacity="0.6"/>
              <path d="M14 14L26 32H2L14 14Z" fill="#29ABE2" opacity="0.6"/>
            </svg>
            <div className="text-white font-bold text-2xl tracking-wide" style={{ fontFamily: "'Playfair Display', serif" }}>
              PEAK VALUE
            </div>
            <div className="text-[#29ABE2] text-sm tracking-[0.3em] uppercase font-medium mt-0.5">
              APPRAISALS
            </div>
          </div>
        </div>

        {/* Card */}
        <div
          className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-8 shadow-2xl"
          style={{ animation: "sectionFadeIn 0.5s ease-out" }}
        >
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#29ABE2]/20 border border-[#29ABE2]/40 mb-4">
              <Lock className="w-5 h-5 text-[#29ABE2]" />
            </div>
            <h1 className="text-white text-xl font-semibold mb-1" style={{ fontFamily: "'Playfair Display', serif" }}>
              Confidential Appraisal Report
            </h1>
            <p className="text-white/60 text-sm">
              {reportData.subject.address}, {reportData.subject.city}, {reportData.subject.state}
            </p>
          </div>

          {/* Expiration notice */}
          {daysLeft > 0 && daysLeft <= 90 && (
            <div className="flex items-center gap-2 bg-[#29ABE2]/10 border border-[#29ABE2]/30 rounded-lg px-3 py-2 mb-5">
              <Clock className="w-4 h-4 text-[#29ABE2] shrink-0" />
              <span className="text-[#29ABE2] text-xs">
                This report expires in <strong>{daysLeft} days</strong> — {reportData.expirationDate.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
              </span>
            </div>
          )}
          {daysLeft === 0 && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-400/30 rounded-lg px-3 py-2 mb-5">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span className="text-red-300 text-xs font-medium">This report has expired. Please contact your appraiser.</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-white/70 text-xs uppercase tracking-wider mb-2">
                Report Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError("");
                }}
                placeholder="Enter your password"
                className={`w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-[#29ABE2] focus:ring-1 focus:ring-[#29ABE2] transition-all font-mono text-sm ${shake ? "animate-[shake_0.5s_ease-in-out]" : ""}`}
                autoFocus
                disabled={daysLeft === 0}
              />
              {error && (
                <div className="flex items-center gap-1.5 mt-2">
                  <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                  <p className="text-red-400 text-xs">{error}</p>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={!password || daysLeft === 0}
              className="w-full bg-[#29ABE2] hover:bg-[#1A9BD0] disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all duration-200 text-sm tracking-wide"
            >
              Access Report
            </button>
          </form>

          <p className="text-center text-white/30 text-xs mt-5">
            Password provided by {reportData.appraiser.company} · {reportData.appraiser.phone}
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-white/25 text-xs mt-6">
          File No. {reportData.fileNo} · Effective {reportData.effectiveDate}
        </p>
      </div>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-8px); }
          40% { transform: translateX(8px); }
          60% { transform: translateX(-6px); }
          80% { transform: translateX(6px); }
        }
      `}</style>
    </div>
  );
}
