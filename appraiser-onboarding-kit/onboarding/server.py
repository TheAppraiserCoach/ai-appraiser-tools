#!/usr/bin/env python3
"""The onboarding server — one process, everything a hire touches.

Routes (browser):
  /onboarding      the hub: checklist of steps, progress, welcome-link identity ingest
  /                the training course (modules + quizzes)
  /agreement-page  read & e-sign the agreement for the hire's track
  /paperwork       tax-form step for the hire's track (upload signed forms)
Routes (data):
  /content.json    compiled course
  /agreement       the agreement body as HTML (owner notes + [CONFIRM] markers stripped)
  /progress?em=    cross-device progress by email
  /health
POSTs:
  /complete        module pass or full-training completion (renders certificate, files it)
  /sign-agreement  e-sign (renders executed agreement PDF, files it)
  /paperwork-upload  signed tax forms (filed to a restricted subfolder)

Design carried over from the system this kit grew out of, learned the hard way:
  - honest status codes: a 200 means "filed", never "received and hoped"
  - server-side progress by email: a hire who switches devices resumes, not restarts
  - per-request temp dirs; no fixed /tmp filenames
  - notifications are best-effort; filing is not
"""
import base64, datetime, json, os, re, shutil, tempfile, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import config as cfgmod, storage as storemod, mailer, render, compile as compilemod

ROOT = cfgmod.ROOT
WEB = os.path.join(ROOT, "web")
TPL = os.path.join(ROOT, "templates")
PROGRESS = os.path.join(WEB, "progress.json")
LOG = os.path.join(ROOT, "server.log")
PROGRESS_LOCK = threading.Lock()

CFG = None      # loaded in main()
STORE = None


def log(m):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {m}"
    print(line)
    try:
        open(LOG, "a").write(line + "\n")
    except OSError:
        pass


# ---------- cross-device progress (keyed by email) ----------
def _pkey(d):
    return (d.get("email") or "").strip().lower()


def progress_update(d, **flags):
    em = _pkey(d)
    if "@" not in em:
        return
    with PROGRESS_LOCK:
        try:
            allp = json.load(open(PROGRESS))
        except Exception:
            allp = {}
        p = allp.setdefault(em, {"modules": {}})
        for k in ("first_name", "last_name", "start_date", "hire_type"):
            if d.get(k):
                p[k] = d[k]
        if flags.get("module") and d.get("score") is not None:
            p["modules"][flags["module"]] = f"{d.get('score')}/{d.get('total')}"
        for k in ("training_done", "agreement_done", "paperwork_done"):
            if flags.get(k):
                p[k] = True
        p["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
        json.dump(allp, open(PROGRESS, "w"), indent=1)


def progress_get(email):
    em = (email or "").strip().lower()
    with PROGRESS_LOCK:
        try:
            p = json.load(open(PROGRESS)).get(em)
        except Exception:
            p = None
    if not p:
        return {"known": False}
    return {"known": True,
            "first_name": p.get("first_name", ""), "last_name": p.get("last_name", ""),
            "start_date": p.get("start_date", ""), "hire_type": p.get("hire_type", ""),
            "modules": p.get("modules", {}),
            "training_done": bool(p.get("training_done")),
            "agreement_done": bool(p.get("agreement_done")),
            "paperwork_done": bool(p.get("paperwork_done"))}


# ---------- agreement rendering ----------
def agreement_html(hire_type_key, extra=None):
    """The agreement body for a track, as HTML — owner notes (> blocks) and [CONFIRM]
    markers stripped: those are author-facing and must never reach a signed document."""
    ht = cfgmod.hire_type(CFG, hire_type_key)
    path = os.path.join(ROOT, "content", "agreements", ht["agreement"])
    raw = open(path).read()
    raw = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith(">"))
    raw = raw.replace("**[CONFIRM]**", "").replace("[CONFIRM]", "")
    filled = cfgmod.fill(raw, CFG, extra or {"full_name": "____________________",
                                             "start_date": "____________"})
    holes = cfgmod.unresolved(filled)
    if holes:
        raise RuntimeError(f"agreement has unresolved placeholders: {holes}")
    # markdown → simple HTML (same buffered parser as the course)
    lines = filled.splitlines()
    html_parts = []
    for chunk in re.split(r'^(#{1,3}\s+.*)$', "\n".join(lines), flags=re.MULTILINE):
        m = re.match(r'^(#{1,3})\s+(.*)', chunk)
        if m:
            tag = "h1" if len(m.group(1)) == 1 else "h2"
            html_parts.append(f"<{tag}>{compilemod.md_inline(m.group(2))}</{tag}>")
        elif chunk.strip():
            html_parts.append(compilemod.body_to_html(chunk.splitlines()))
    return "\n".join(html_parts)


# ---------- filing helpers ----------
def _workdir():
    return tempfile.mkdtemp(prefix="onbkit_")


def file_certificate(d):
    """Full training completion → certificate PDF → hire folder + notify owner."""
    work = _workdir()
    try:
        results = d.get("results", {})
        rows = "\n".join(
            f"<tr><td>{compilemod.md_inline(mid)}</td><td>{compilemod.md_inline(str(score))}</td></tr>"
            for mid, score in results.items())
        now = datetime.datetime.now()
        html = cfgmod.fill(open(os.path.join(TPL, "certificate.html")).read(), CFG, {
            "full_name": f"{d.get('first_name','')} {d.get('last_name','')}".strip(),
            "email": d.get("email", ""), "start_date": d.get("start_date", ""),
            "completed_date": now.strftime("%B %-d, %Y"),
            "module_rows": rows,
            "attestation_text": d.get("attestation_text", ""),
            "record_id": now.strftime("TR%Y%m%d%H%M%S")})
        out = render.html_to_pdf(html, os.path.join(work, "Training_Certificate.pdf"))
        dest = STORE.put(d, out)
        STORE.upsert(d, training="Complete")
        emp = d.get("email", "")
        body = (f"{d.get('first_name','')} {d.get('last_name','')} completed all onboarding "
                f"training modules with passing scores. Certificate attached and filed.")
        mailer.send(CFG, emp or CFG["people"]["owner"]["email"],
                    f"Training complete — {CFG['office']['name']}", body, attachments=[out],
                    cc=CFG["people"]["owner"]["email"] if emp else None)
        log(f"certificate filed for {d.get('first_name')} {d.get('last_name')} -> {dest}")
        return True
    except Exception as e:
        log(f"certificate FAILED: {e}")
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def file_signed_agreement(d, ip):
    work = _workdir()
    try:
        signed = d.get("completed_date") or datetime.date.today().isoformat()
        rid = datetime.datetime.now().strftime("AG%Y%m%d%H%M%S")
        body = agreement_html(d.get("hire_type"), {
            "full_name": f"{d.get('first_name','')} {d.get('last_name','')}".strip(),
            "start_date": d.get("start_date", "")})
        e = lambda s: compilemod.H.escape(str(s or ""))
        block = [
            '<div class="sigwrap">',
            '<div class="sigrow"><span class="lbl">Signed by</span><br>',
            f'<span class="sig">{e(d.get("signature_typed") or d.get("first_name","") + " " + d.get("last_name",""))}</span>',
            f'<div class="meta">Printed name: {e(d.get("first_name",""))} {e(d.get("last_name",""))}'
            f' &nbsp;|&nbsp; Date signed: {e(signed)}</div>',
            f'<div class="meta">Address: {e(d.get("employee_address")) or "&mdash;"}</div></div>',
            f'<div class="sigrow"><span class="lbl">For {e(CFG["office"]["name"])}</span><br>',
            f'<span class="sig">{e(CFG["people"]["owner"]["name"])}</span>',
            f'<div class="meta">{e(CFG["people"]["owner"]["name"])}, {e(CFG["people"]["owner"]["title"])}'
            f' &nbsp;|&nbsp; Countersigned electronically {e(signed)}</div></div>',
        ]
        if str(d.get("is_minor", "")).lower() in ("yes", "true", "1"):
            block += [
                '<div class="sigrow"><span class="lbl">Parent / Legal Guardian (signer is under 18)</span><br>',
                f'<span class="sig">{e(d.get("parent_signature") or d.get("parent_name"))}</span>',
                f'<div class="meta">Printed name: {e(d.get("parent_name"))} &nbsp;|&nbsp; '
                f'Relationship: {e(d.get("parent_relationship"))} &nbsp;|&nbsp; Date: {e(signed)}</div></div>']
        att = d.get("attestation_text") or "Electronically signed via the onboarding portal."
        block.append(
            f'<div class="esign"><b>Electronic signature record.</b> {e(att)} '
            f'Signed {e(signed)} from IP {e(ip or "n/a")}. Record ID {e(rid)}. '
            f'Under the federal ESIGN Act and applicable state law (UETA), this electronic '
            f'signature has the same legal effect as a handwritten signature.</div></div>')
        html = cfgmod.fill(open(os.path.join(TPL, "signed-agreement.html")).read(), CFG, {
            "agreement_body": body, "signature_block": "\n".join(block)})
        out = render.html_to_pdf(html, os.path.join(work, "Signed_Agreement.pdf"))
        dest = STORE.put(d, out)
        STORE.upsert(d, agreement="Signed")
        mailer.notify_owner(CFG, f"Agreement signed — {d.get('first_name')} {d.get('last_name')}",
                            f"The executed agreement is attached and filed.", attachments=[out])
        log(f"agreement filed for {d.get('first_name')} {d.get('last_name')} -> {dest}")
        return True
    except Exception as e2:
        log(f"agreement FAILED: {e2}")
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def file_paperwork(d):
    """Signed tax forms → restricted subfolder. These carry SSNs/bank details."""
    work = _workdir()
    try:
        OK_EXT = (".pdf", ".png", ".jpg", ".jpeg", ".heic", ".webp")
        made, paths = [], []
        for f in (d.get("files") or []):
            b64 = f.get("content_b64") or ""
            if not b64:
                continue
            doc = re.sub(r"[^A-Za-z0-9]+", "", f.get("doc", "Doc")) or "Doc"
            ext = os.path.splitext(f.get("filename", ""))[1].lower()
            if ext not in OK_EXT:
                ext = ".pdf"
            out = os.path.join(work, f"Paperwork_{doc}{ext}")
            with open(out, "wb") as fh:
                fh.write(base64.b64decode(b64))
            STORE.put(d, out, subfolder="_paperwork")
            made.append(doc)
            paths.append(out)
        if not made:
            return False
        STORE.upsert(d, tax_forms=", ".join(made))
        bk = CFG["people"].get("bookkeeper", {}).get("email", "")
        body = (f"{d.get('first_name','')} {d.get('last_name','')} submitted signed paperwork "
                f"({', '.join(made)}) — attached, and filed in their record's _paperwork folder. "
                f"These attachments contain sensitive information; handle accordingly.")
        mailer.send(CFG, CFG["people"]["owner"]["email"],
                    f"Paperwork submitted — {d.get('first_name')} {d.get('last_name')}",
                    body, attachments=paths, cc=bk or None)
        log(f"paperwork filed for {d.get('first_name')} {d.get('last_name')}: {', '.join(made)}")
        return True
    except Exception as e:
        log(f"paperwork FAILED: {e}")
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def maybe_complete(d):
    row = STORE.status(d) or {}
    done = (row.get("training") == "Complete" and row.get("agreement") == "Signed"
            and bool(row.get("tax_forms")))
    STORE.upsert(d, complete="YES" if done else "")
    if done:
        mailer.notify_owner(CFG, f"Onboarding COMPLETE — {d.get('first_name')} {d.get('last_name')}",
                            "Training, agreement, and paperwork are all in. Cleared to start"
                            + (" — remember the in-person ID check on their first shift (I-9)."
                               if cfgmod.hire_type(CFG, d.get("hire_type", "")).get(
                                   "requires_inperson_id_check") else "."))
    return done


# ---------- HTTP ----------
def serve_page(name):
    raw = open(os.path.join(WEB, name)).read()
    ht = cfgmod.enabled_hire_types(CFG)
    return cfgmod.fill(raw, CFG, {
        "hire_types_json": json.dumps({k: {"label": v["label"], "tax_forms": v["tax_forms"],
                                           "id_check": v.get("requires_inperson_id_check", False)}
                                       for k, v in ht.items()}),
        "default_hire_type": next(iter(ht), "")})


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(b)

    def _client_ip(self):
        fwd = self.headers.get("CF-Connecting-IP") or self.headers.get("X-Forwarded-For")
        return (fwd.split(",")[0].strip() if fwd else self.client_address[0])

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        try:
            if path == "/":
                self._send(200, serve_page("course.html"))
            elif path == "/onboarding":
                self._send(200, serve_page("hub.html"))
            elif path == "/agreement-page":
                self._send(200, serve_page("agreement.html"))
            elif path == "/paperwork":
                self._send(200, serve_page("paperwork.html"))
            elif path == "/content.json":
                # ?ht=<hire type> picks that track's course. Unknown or missing falls back
                # to the office-wide one rather than 404ing a hire out of their training.
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                ht = (q.get("ht") or [""])[0]
                src = compilemod.course_path(ht if ht in cfgmod.enabled_hire_types(CFG) else None)
                if not os.path.exists(src):
                    src = compilemod.course_path(None)
                self._send(200, open(src, "rb").read(), "application/json")
            elif path == "/agreement":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                ht = (q.get("type") or [""])[0] or next(iter(cfgmod.enabled_hire_types(CFG)))
                self._send(200, agreement_html(ht))
            elif path == "/progress":
                q = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
                self._send(200, json.dumps(progress_get((q.get("em") or [""])[0])),
                           "application/json")
            elif path == "/health":
                self._send(200, json.dumps({"ok": True, "office": CFG["office"]["name"],
                                            "storage": STORE.describe()}), "application/json")
            else:
                self._send(404, "not found")
        except Exception as e:
            log(f"GET {path} error: {e}")
            self._send(500, "server error")

    def do_POST(self):
        route = self.path.rstrip("/")
        if route not in ("/complete", "/sign-agreement", "/paperwork-upload"):
            self._send(404, "not found")
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self._send(400, '{"ok":false}', "application/json")
            return
        if route == "/paperwork-upload":
            ok = file_paperwork(d)
            if ok:
                progress_update(d, paperwork_done=True)
                maybe_complete(d)
            self._send(200 if ok else 502, json.dumps({"ok": bool(ok)}), "application/json")
            return
        if route == "/sign-agreement":
            ok = file_signed_agreement(d, self._client_ip())
            if ok:
                progress_update(d, agreement_done=True)
                maybe_complete(d)
            self._send(200 if ok else 502, json.dumps({"ok": bool(ok)}), "application/json")
            return
        # /complete
        if d.get("module") == "ALL":
            ok = file_certificate(d)
            if ok:
                progress_update(d, training_done=True)
                maybe_complete(d)
            self._send(200 if ok else 502, json.dumps({"ok": bool(ok)}), "application/json")
            return
        if d.get("module"):
            progress_update(d, module=d.get("module"))
        self._send(200, json.dumps({"ok": True}), "application/json")


def main():
    global CFG, STORE
    CFG = cfgmod.load()
    STORE = storemod.get(CFG)
    compilemod.compile_all(CFG)         # course always matches current content + config
    port = int(CFG.get("server", {}).get("port", 8620))
    log(f"onboarding server for {CFG['office']['name']} on :{port} "
        f"(storage: {STORE.describe()}, email: {CFG['email']['mode']})")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
