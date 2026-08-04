"""Compile the markdown training modules into the course's content.json.

Reads the module list from config (so an office adds/removes/reorders modules by editing
office.json, not code), fills {{placeholders}}, and parses each module into lessons +
quiz. The parser buffers hard-wrapped lines — bold spans and quiz questions that wrap
onto a second line render correctly (this bug shipped once in an earlier life; the fix
is kept).

Usage: python3 -m onboarding.compile        (writes web/content.json)
"""
import json, os, re, html as H

from . import config as cfgmod

ROOT = cfgmod.ROOT
SRC = os.path.join(ROOT, "content", "training")
OUT = os.path.join(ROOT, "web", "content.json")


def md_inline(s):
    s = H.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s


def body_to_html(lines):
    """Markdown-ish → HTML with hard-wrap awareness: bullets/paragraphs are buffered
    until they really end so md_inline sees whole logical lines."""
    out, para, item, items = [], [], None, []

    def close_list():
        nonlocal items
        if items:
            out.append("<ul>" + "\n".join("<li>" + md_inline(t) + "</li>" for t in items) + "</ul>")
            items = []

    def flush_item():
        nonlocal item
        if item is not None:
            items.append(item)
            item = None

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para = []

    for ln in lines:
        s = ln.strip()
        if s == "---":
            continue
        m = re.match(r'^(#{2,3})\s+(.*)', ln)          # ## / ### subheads inside a lesson
        if m:
            flush_para(); flush_item(); close_list()
            out.append(f"<h4>{md_inline(m.group(2))}</h4>")
            continue
        lm = re.match(r'^[-*]\s+(.*)', ln)
        if lm:
            flush_para(); flush_item()
            item = lm.group(1)
            continue
        if not s:                                       # blank line ends everything open
            flush_para(); flush_item(); close_list()
            continue
        if item is not None and ln.startswith("  "):    # wrapped continuation of a bullet
            item += " " + s
            continue
        if re.match(r'^\d+\.\s', s):                    # numbered step = its own paragraph
            flush_para(); flush_item(); close_list()
            para.append(s)
            continue
        flush_item(); close_list()
        para.append(s)
    flush_para(); flush_item(); close_list()
    return "\n".join(out)


def compile_module(path, cfg):
    raw = cfgmod.fill(open(path).read(), cfg)
    raw = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith(">"))  # drop owner notes
    qm = re.search(r'^#\s+.*Quiz.*$', raw, re.MULTILINE)
    lessons_src = raw[:qm.start()] if qm else raw
    quiz_src = raw[qm.start():] if qm else ""

    tm = re.search(r'^#\s+(.*)$', lessons_src, re.MULTILINE)
    title = tm.group(1).strip() if tm else os.path.basename(path)

    lessons = []
    parts = re.split(r'^##\s+(.*)$', lessons_src, flags=re.MULTILINE)
    intro = re.sub(r'^#\s+.*$', '', parts[0], count=1, flags=re.MULTILINE).strip()
    if intro:
        lessons.append({"title": "Welcome", "html": body_to_html(intro.splitlines())})
    for i in range(1, len(parts), 2):
        head = re.sub(r'^\d+\.\s*', '', parts[i].strip())
        body = parts[i + 1] if i + 1 < len(parts) else ""
        lessons.append({"title": head, "html": body_to_html(body.splitlines())})

    # quiz — questions AND options may hard-wrap; join before use
    quiz = []
    for qblock in re.split(r'\*\*Q\d+\.\s*', quiz_src)[1:]:
        qlines, options, correct, in_opts = [], [], 0, False
        for ln in qblock.splitlines():
            om = re.match(r'^\s*-\s*[A-D]\)\s*(.*)', ln)
            if om:
                in_opts = True
                txt = om.group(1)
                if "✅" in txt:
                    correct = len(options)
                    txt = txt.replace("✅", "").strip()
                options.append(txt.strip())
            elif in_opts:
                if ln.strip() and not ln.strip().startswith(("*", "#", "-")):
                    options[-1] += " " + ln.strip()
            elif ln.strip():
                qlines.append(ln.strip())
        question = " ".join(qlines).replace("**", "").strip()
        if options:
            quiz.append({"q": md_inline(question),
                         "options": [md_inline(o) for o in options],
                         "correct": correct})
    return {"title": title, "lessons": lessons, "quiz": quiz}


def course_path(hire_type_key=None):
    """Where a track's compiled course lives. The unsuffixed content.json stays the
    office-wide default so an older link, or a hire filed before tracks existed, still
    loads something."""
    if not hire_type_key:
        return OUT
    return os.path.join(ROOT, "web", f"content.{hire_type_key}.json")


def _compile_list(cfg, module_files):
    modules = []
    for fn in module_files:
        c = compile_module(os.path.join(SRC, fn), cfg)
        c["id"] = re.sub(r'^\d+-|\.md$', '', fn)
        modules.append(c)
    return {"modules": modules,
            "require_perfect": bool(cfg.get("training", {}).get("require_perfect_score", True))}


def compile_all(cfg=None):
    """Write the default course plus one per enabled hire type. Returns
    {hire_type_key_or_None: compiled}. Tracks that use the office-wide module list still
    get their own file — one fewer conditional at read time, and it stays correct if the
    office later gives that track its own modules."""
    cfg = cfg or cfgmod.load()
    os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
    results = {}
    for key in [None] + list(cfgmod.enabled_hire_types(cfg)):
        out = _compile_list(cfg, cfgmod.training_modules(cfg, key))
        json.dump(out, open(course_path(key), "w"), indent=1)
        results[key] = out
    return results


if __name__ == "__main__":
    cfg = cfgmod.load()
    for key, out in compile_all(cfg).items():
        print(f"\n--- {key or 'default (office-wide list)'} → {os.path.basename(course_path(key))}")
        for m in out["modules"]:
            print(f"  {m['id']:30s} {len(m['lessons'])} lessons, {len(m['quiz'])} quiz Qs — {m['title']}")
