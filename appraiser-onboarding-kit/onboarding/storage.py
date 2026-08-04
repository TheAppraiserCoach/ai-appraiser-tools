"""Where completed onboarding records go.

Two backends, same interface:
  local  — a folder per hire on this machine + a CSV tracker. No Google account, no API
           keys, nothing to authorize. This is the default and it is enough for an office
           that hires a few people a year.
  google — a folder per hire in Google Drive + a tracker Sheet, via the `gog` CLI.

Records contain SSNs and bank details. Whichever backend you use, the destination must be
somewhere only the people who handle payroll can reach.
"""
import csv, datetime, json, os, re, shutil, subprocess

from . import config as cfgmod

TRACKER_COLUMNS = ["hire", "email", "hire_type", "start_date", "agreement",
                   "tax_forms", "training", "complete", "last_update"]


def _slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", (s or "").strip()).strip("_") or "unnamed"


def folder_name(hire):
    return f"{_slug(hire.get('last_name'))}_{_slug(hire.get('first_name'))}"


def get(cfg):
    mode = cfg.get("storage", {}).get("mode", "local")
    return GoogleStorage(cfg) if mode == "google" else LocalStorage(cfg)


class LocalStorage:
    """Files on this machine. Simplest possible thing that actually works."""

    def __init__(self, cfg):
        self.cfg = cfg
        root = cfg["storage"].get("local_root", "./records")
        if not os.path.isabs(root):
            root = os.path.join(cfgmod.ROOT, root)
        self.root = root
        self.tracker = os.path.join(self.root, "tracker.csv")
        os.makedirs(self.root, exist_ok=True)
        # 0700: the parent directory holds tax documents.
        try:
            os.chmod(self.root, 0o700)
        except OSError:
            pass

    def describe(self):
        return f"local folder {self.root}"

    def hire_folder(self, hire, subfolder=None):
        p = os.path.join(self.root, folder_name(hire))
        if subfolder:
            p = os.path.join(p, subfolder)
        os.makedirs(p, exist_ok=True)
        return p

    def put(self, hire, local_path, subfolder=None):
        dest_dir = self.hire_folder(hire, subfolder)
        dest = os.path.join(dest_dir, os.path.basename(local_path))
        shutil.copy(local_path, dest)
        return dest

    def _rows(self):
        if not os.path.exists(self.tracker):
            return []
        with open(self.tracker, newline="") as f:
            return list(csv.DictReader(f))

    def _write(self, rows):
        tmp = self.tracker + ".tmp"
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TRACKER_COLUMNS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in TRACKER_COLUMNS})
        os.replace(tmp, self.tracker)

    def upsert(self, hire, **fields):
        rows = self._rows()
        key = folder_name(hire)
        row = next((r for r in rows if r.get("hire") == key), None)
        if row is None:
            row = {"hire": key, "email": hire.get("email", ""),
                   "hire_type": hire.get("hire_type", ""),
                   "start_date": hire.get("start_date", "")}
            rows.append(row)
        row.update({k: v for k, v in fields.items() if v is not None})
        row["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self._write(rows)
        return row

    def status(self, hire):
        key = folder_name(hire)
        return next((r for r in self._rows() if r.get("hire") == key), None)


class GoogleStorage:
    """Drive folders + a tracker Sheet through the `gog` CLI. Only for offices already
    living in Google Workspace; `local` is the better default for everyone else."""

    def __init__(self, cfg):
        self.cfg = cfg
        g = cfg["storage"]["google"]
        self.account = g["account"]
        self.parent = g["employees_folder_id"]
        self.sheet = g["tracker_sheet_id"]
        self.tab = g.get("tracker_tab", "Hires")
        self.bin = cfg.get("email", {}).get("gog", {}).get("binary", "gog")

    def describe(self):
        return f"Google Drive folder {self.parent} + tracker sheet {self.sheet}"

    def _run(self, args, json_out=False):
        r = subprocess.run([self.bin] + args + (["--json"] if json_out else []),
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"gog {' '.join(args[:2])} failed: {r.stderr.strip()[:300]}")
        return json.loads(r.stdout) if json_out and r.stdout.strip() else r.stdout

    def _find_child(self, parent, name, folder=False):
        safe = name.replace("\\", "\\\\").replace("'", "\\'")   # O'Brien breaks the query
        res = self._run(["drive", "search", "--account", self.account,
                         f"'{parent}' in parents and name = '{safe}' and trashed = false"],
                        json_out=True)
        items = res if isinstance(res, list) else res.get("files", res.get("results", []))
        for it in items:
            is_f = it.get("mimeType") == "application/vnd.google-apps.folder"
            if it.get("name") == name and (is_f if folder else True):
                return it.get("id")
        return None

    def _ensure_folder(self, name, parent):
        fid = self._find_child(parent, name, folder=True)
        if fid:
            return fid
        out = self._run(["drive", "mkdir", name, "--parent", parent,
                         "--account", self.account])
        for tok in out.split():
            if len(tok) > 20 and "/" not in tok:
                return tok
        return self._find_child(parent, name, folder=True)

    def hire_folder(self, hire, subfolder=None):
        fid = self._ensure_folder(folder_name(hire), self.parent)
        return self._ensure_folder(subfolder, fid) if subfolder else fid

    def put(self, hire, local_path, subfolder=None):
        fid = self.hire_folder(hire, subfolder)
        name = os.path.basename(local_path)
        existing = self._find_child(fid, name)
        if existing:
            self._run(["drive", "update", existing, local_path, "--account", self.account])
            return existing
        self._run(["drive", "upload", local_path, "--parent", fid, "--account", self.account])
        return self._find_child(fid, name)

    def _sheet_rows(self):
        out = self._run(["sheets", "get", "--account", self.account, self.sheet,
                         f"{self.tab}!A1:I200", "--json"], json_out=False)
        try:
            return json.loads(out).get("values", [])
        except Exception:
            return []

    def upsert(self, hire, **fields):
        rows = self._sheet_rows()
        key = folder_name(hire)
        header = rows[0] if rows else TRACKER_COLUMNS
        idx = next((i for i, r in enumerate(rows[1:], start=2) if r and r[0] == key), None)
        record = {"hire": key, "email": hire.get("email", ""),
                  "hire_type": hire.get("hire_type", ""),
                  "start_date": hire.get("start_date", "")}
        if idx:
            existing = rows[idx - 1] + [""] * len(header)
            record = {h: existing[i] for i, h in enumerate(header) if i < len(existing)}
        record.update({k: v for k, v in fields.items() if v is not None})
        record["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        line = [record.get(c, "") for c in TRACKER_COLUMNS]
        if idx:
            self._run(["sheets", "update", "--account", self.account, self.sheet,
                       f"{self.tab}!A{idx}:I{idx}"] + line)
        else:
            self._run(["sheets", "append", "--account", self.account, self.sheet,
                       f"{self.tab}!A:I"] + line)
        return record

    def status(self, hire):
        rows = self._sheet_rows()
        if not rows:
            return None
        header = rows[0]
        key = folder_name(hire)
        for r in rows[1:]:
            if r and r[0] == key:
                return {h: (r[i] if i < len(r) else "") for i, h in enumerate(header)}
        return None
