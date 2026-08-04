"""Turn HTML into a PDF for the permanent record.

Finds a Chrome/Chromium on the machine instead of assuming a path. If there isn't one,
falls back to saving the styled HTML itself — a signed record you can open in any browser
beats a crash. (The tracker notes which format was produced.)
"""
import os, re, shutil, subprocess, tempfile

_CHROME_CANDIDATES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/chromium", "/usr/bin/google-chrome",
    "/opt/openclaw/.agent-browser/browsers/chrome-146.0.7680.153/chrome",
]


def find_chrome():
    for c in _CHROME_CANDIDATES:
        p = shutil.which(c) if not c.startswith("/") else (c if os.path.exists(c) else None)
        if p:
            return p
    return None


def html_to_pdf(html_str, out_pdf, retries=3):
    """Render HTML to PDF. Returns the path actually written: out_pdf on success, or an
    .html fallback next to it if no Chrome exists or rendering fails."""
    chrome = find_chrome()
    fallback = re.sub(r"\.pdf$", ".html", out_pdf)
    if not chrome:
        open(fallback, "w").write(html_str)
        return fallback
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html_str)
        src = f.name
    try:
        for attempt in range(retries):
            r = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                 "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}", f"file://{src}"],
                capture_output=True, timeout=60)
            if r.returncode == 0 and os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 500:
                return out_pdf
        open(fallback, "w").write(html_str)   # chrome flaked repeatedly — keep the record anyway
        return fallback
    finally:
        os.unlink(src)
